"""Lavish owner video, grown-up look + motion.
Clean bars (yellow / black / off-white), slide-in with motion blur + overshoot, living hold (drift),
count-ups, light sweep, text roll (morph in place), camera pushes, hook title behind the owner, QR tile, logo end card.
Reads master.mkv by frame index (exact sync), writes gfx.mkv (video only)."""
import sys, json, subprocess, math, numpy as np, cv2, mediapipe as mp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mediapipe.tasks.python import vision, BaseOptions

S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
J = S + "/job5"
sys.path.insert(0, J)
from plan import P, out_time, piece_out, TOTAL, LOGO

W, H, FPS = 1080, 1920, 30
YEL, BEI, INK = (240, 204, 56), (252, 240, 228), (17, 17, 17)
BEBAS = "/home/user/Claude-get-know-me/assets/fonts/BebasNeue-Regular.ttf"
HEAD = S + "/font/rubik900.ttf"          # placeholder for the owner's headline font (Co Moderno)
LOGO_PNG = "/home/user/Claude-get-know-me/assets/logo-beige.png"
X0 = 64                                   # left grid line

def font(path, size): return ImageFont.truetype(path, size)
def ease_back(p, c=1.9):
    p = min(1.0, max(0.0, p)); return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2
def ease_out(p): p = min(1.0, max(0.0, p)); return 1 - (1 - p) ** 3
def ease_in(p): p = min(1.0, max(0.0, p)); return p ** 3

# ---------------- drawing helpers ----------------
def text_img(text, size, color, path=BEBAS, track=1.5):
    f = font(path, size)
    w = int(sum(f.getlength(c) + track for c in text)) + 4
    asc, desc = f.getmetrics()
    im = Image.new("RGBA", (max(2, w), asc + desc), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 0
    for c in text:
        d.text((x, 0), c, font=f, fill=color + (255,)); x += f.getlength(c) + track
    return im

def cap_box(size, path=BEBAS):
    f = font(path, size); b = f.getbbox("H"); return b[1], b[3]      # top/bottom of capitals

STY = {"Y": (YEL, INK), "K": (INK, BEI), "W": (BEI, INK)}

def bar_canvas(w, h, style):
    return Image.new("RGBA", (int(w), int(h)), STY[style][0] + (255,))

def bar_metrics(size):
    top, bot = cap_box(size); caph = bot - top
    h = int(round(caph * 1.62)); pad = int(round(caph * 0.50))
    return h, pad, top, caph

def make_bar(text, style, size=74):
    h, pad, top, caph = bar_metrics(size)
    t = text_img(text, size, STY[style][1])
    im = bar_canvas(t.width + 2 * pad, h, style)
    im.alpha_composite(t, (pad, (h - caph) // 2 - top))
    return im

def shadowed(im, blur=10, off=(0, 8), strength=95, pad=60):
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * strength / 255))
    sh.paste((0, 0, 0, 255), (pad + off[0], pad + off[1]), a)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); out.alpha_composite(im, (pad, pad))
    return out, pad

def mblur(im, dx, dy):
    """directional motion blur for an RGBA tile (premultiplied)"""
    k = int(max(abs(dx), abs(dy)) * 0.9)
    if k < 3: return im
    a = np.array(im).astype(np.float32); a[..., :3] *= a[..., 3:4] / 255
    a = cv2.blur(a, (k, 1) if abs(dx) >= abs(dy) else (1, k))
    al = np.maximum(a[..., 3:4], 1e-3); a[..., :3] = a[..., :3] / al * 255
    return Image.fromarray(a.clip(0, 255).astype("uint8"))

def sweep(im, p):
    """one light streak travelling over the bar, p in 0..1"""
    w, h = im.size
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    c = -0.25 * w + p * 1.5 * w
    band = np.exp(-(((xx + 0.55 * yy) - c) / 34.0) ** 2) * 0.42
    a = np.array(im).astype(np.float32)
    a[..., :3] += (255 - a[..., :3]) * band[..., None]
    return Image.fromarray(a.clip(0, 255).astype("uint8"))

# ---------------- elements ----------------
class El:
    """content(t_local) -> RGBA tile; handles enter / living hold / exit"""
    def __init__(self, t_in, t_out, x, y, content, enter=(-1, 0), exit=(-1, 0), dist=300, din=0.28, dout=0.17,
                 drift=(7, 0), do_sweep=False, cut_out=False, move=None, shadow=True):
        self.__dict__.update(locals())
    def draw(self, layer, t):
        if not (self.t_in <= t < self.t_out): return
        tl = t - self.t_in; life = self.t_out - self.t_in
        im = self.content(tl)
        if self.do_sweep and 0.34 <= tl < 0.34 + 0.5:
            im = sweep(im, (tl - 0.34) / 0.5)
        im, pad = shadowed(im) if self.shadow else (im.copy(), 0)   # copy: never alter a cached image
        p = tl / self.din
        ox = oy = 0.0; vx = vy = 0.0; alpha = 1.0
        if p < 1:
            k = 1 - ease_back(p); k2 = 1 - ease_back(min(1, p + 1 / (self.din * FPS)))
            ox, oy = self.enter[0] * self.dist * k, self.enter[1] * self.dist * k
            vx, vy = self.enter[0] * self.dist * (k - k2), self.enter[1] * self.dist * (k - k2)
            alpha = min(1.0, p * 3.2)
        q = (t - (self.t_out - self.dout)) / self.dout
        if q > 0 and not self.cut_out:
            k = ease_in(q); k2 = ease_in(min(1, q + 1 / (self.dout * FPS)))
            ox += self.exit[0] * self.dist * k; oy += self.exit[1] * self.dist * k
            vx, vy = self.exit[0] * self.dist * (k2 - k), self.exit[1] * self.dist * (k2 - k)
            alpha = min(alpha, 1 - max(0, (q - 0.55) / 0.45))
        dr = min(1.0, tl / max(life, 0.01))
        ox += self.drift[0] * dr; oy += self.drift[1] * dr
        if self.move:
            mx, my = self.move(tl); ox += mx; oy += my
        im = mblur(im, vx, vy)
        if alpha < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        layer.alpha_composite(im, (int(round(self.x + ox)) - pad, int(round(self.y + oy)) - pad)) if \
            -pad < self.x + ox < W and -pad < self.y + oy < H else None

def static(im): return lambda tl: im

def rolling_bar(states, style, size=74, dur=0.24):
    """states: [(t_local, text)] -> the text rolls upward into the next one, the bar width follows"""
    h, pad, top, caph = bar_metrics(size)
    tx = [text_img(s, size, STY[style][1]) for _, s in states]
    def content(tl):
        i = max(k for k, (ts, _) in enumerate(states) if tl >= ts)
        ts = states[i][0]
        p = ease_out((tl - ts) / dur) if i > 0 else 1.0
        w_new = tx[i].width + 2 * pad
        w_old = tx[i - 1].width + 2 * pad if i > 0 else w_new
        w = int(round(w_old + (w_new - w_old) * p))
        im = bar_canvas(max(w_old, w_new), h, style); y0 = (h - caph) // 2 - top
        if p < 1:
            im.alpha_composite(tx[i - 1], (pad, int(y0 - h * p)))
            im.alpha_composite(tx[i], (pad, int(y0 + h * (1 - p))))
        else:
            im.alpha_composite(tx[i], (pad, y0))
        return im.crop((0, 0, w, h))
    return content

def count_bar(prefix_fn, final_n, suffix, style, size=74, dur=0.55):
    """number counts up inside a bar; bar width is fixed to the final width"""
    h, pad, top, caph = bar_metrics(size)
    cell = text_img(str(final_n), size, STY[style][1]).width
    suf = text_img(suffix, size, STY[style][1])
    def content(tl):
        n = int(round(final_n * ease_out(tl / dur)))
        num = text_img(str(n), size, STY[style][1])
        im = bar_canvas(cell + suf.width + 2 * pad, h, style); y0 = (h - caph) // 2 - top
        im.alpha_composite(num, (pad + cell - num.width, y0)); im.alpha_composite(suf, (pad + cell, y0))
        return im
    return content

def framed(path, w, b=8):
    im = Image.open(path).convert("RGB"); im = im.resize((w, int(round(w * im.height / im.width))), Image.LANCZOS)
    out = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), INK + (255,)); out.paste(im, (b, b)); return out

def outline(w, h, t=6):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=YEL + (255,), width=t); return im

def timer_block(t_count, dur=0.9):
    """black block: small label + big yellow seconds counter"""
    lab = text_img("POP-UP NACH", 50, BEI, track=3)
    sek = text_img("SEKUNDEN", 50, BEI, track=3)
    top, bot = cap_box(250); caph = bot - top
    wnum = text_img("10", 250, YEL).width
    bw, bh = 44 + max(lab.width, wnum + 18 + sek.width) + 44, 40 + 30 + 22 + caph + 40
    ltop, lbot = cap_box(50)
    def content(tl):
        n = int(round(10 * min(1.0, max(0.0, (tl - t_count) / dur))))
        im = Image.new("RGBA", (bw, bh), INK + (255,))
        im.alpha_composite(lab, (44, 40 - ltop))
        num = text_img(str(n), 250, YEL)
        im.alpha_composite(num, (44 + wnum - num.width, 40 + 30 + 22 - top))
        im.alpha_composite(sek, (44 + wnum + 18, 40 + 30 + 22 + caph - (lbot - ltop) - ltop))
        return im
    return content

def qr_tile(size=348):
    q = Image.open(J + "/qr_clean.png").convert("L").resize((size, size), Image.LANCZOS)
    b = 10
    im = Image.new("RGBA", (size + 2 * b, size + 2 * b), INK + (255,))
    im.paste(Image.merge("RGBA", (q, q, q, Image.new("L", q.size, 255))), (b, b))
    return im

# ---------------- timeline (output seconds) ----------------
o = out_time
E = []                                  # front elements
BIG, MID, TAG = 96, 70, 46
hb = bar_metrics(BIG)[0]; hm = bar_metrics(MID)[0]; ht = bar_metrics(TAG)[0]; GAP = 12
Y1 = 300; RW = Y1 + hb + GAP; CW = 360
IMG = J + "/img/"
SHAKE = []                              # (t0, dur, amplitude px): camera hits
def pop_card(im, k0=0.82, c=2.0, dur=0.26):
    def content(tl):
        k = k0 + (1 - k0) * ease_back(tl / dur, c) if k0 < 1 else 1 + (k0 - 1) * (1 - ease_out(tl / dur))
        r = im.resize((max(2, int(im.width * k)), max(2, int(im.height * k))), Image.LANCZOS)
        cv = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if k <= 1: cv.alpha_composite(r, ((im.width - r.width) // 2, (im.height - r.height) // 2))
        else:
            x = (r.width - im.width) // 2; y = (r.height - im.height) // 2; cv.paste(r.crop((x, y, x + im.width, y + im.height)))
        return cv
    return content
def popped(path, w, t0, t1, x, y, b=8, drift=(0, 4)):
    E.append(El(t0, t1, x, y, pop_card(framed(path, w, b)), enter=(0, 0), dist=0, din=0.10, dout=0.10, drift=drift))
def slam(im, dur=0.16):
    """big -> normal in a few frames (hard hit instead of a soft fade)"""
    return pop_card(im, k0=1.45, dur=dur)
def struck_bar(text, style, size, t_strike, dur=0.24):
    base = make_bar(text, style, size); h = base.height
    def content(tl):
        im = slam(base)(tl)
        p = ease_out((tl - t_strike) / dur)
        if p > 0:
            d = ImageDraw.Draw(im); x1 = int(16 + (im.width - 32) * p); th = max(8, h // 9); y = h // 2 - th // 2
            d.rectangle((16, y, x1, y + th), fill=YEL + (255,))
        if tl > t_strike + dur:                              # after the strike the old word steps back a little
            a = im.getchannel("A").point(lambda v: int(v * 0.82)); im.putalpha(a)
        return im
    return content
def q_card(n, w=104, h=136, t_flip=0.0, dur=0.26):
    f = font(HEAD, 96); fs = font(BEBAS, 26)
    card = Image.new("RGBA", (w, h), INK + (255,)); d = ImageDraw.Draw(card)
    d.rectangle((0, 0, w - 1, h - 1), outline=YEL + (255,), width=4)
    qw = f.getlength("?"); d.text(((w - qw * 0.8) / 2 - 4, 4), "?", font=f, fill=BEI + (255,))
    lab = f"0{n}"; d.text(((w - fs.getlength(lab)) / 2, h - 34), lab, font=fs, fill=YEL + (255,))
    def content(tl):
        p = ease_back((tl - t_flip) / dur, 1.6)
        sx = max(0.02, min(1.12, p)); im = card.resize((max(2, int(w * sx)), h), Image.LANCZOS)
        cv = Image.new("RGBA", (int(w * 1.12) + 2, h), (0, 0, 0, 0)); cv.alpha_composite(im, ((cv.width - im.width) // 2, 0))
        return cv
    return content

END = TOTAL
po = piece_out
def card_seq(paths, t0, t1, x, y, w=CW, b=8):
    n = len(paths); d = (t1 - t0) / n
    for i, p in enumerate(paths):
        popped(IMG + p + ".png", w, t0 + i * d, t0 + (i + 1) * d + (0.08 if i == n - 1 else 0.0), x, y, b=b, drift=(0, 3))
def video_card(folder, start, fps=30, b=8):
    import glob
    fr = sorted(glob.glob(folder + "/*.png")); first = Image.open(fr[0])
    def content(tl):
        i = min(len(fr) - 1, int((start + tl) * fps)); im = Image.open(fr[i]).convert("RGB")
        out = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), INK + (255,)); out.paste(im, (b, b)); return out
    return content, first.width + 2 * b, first.height + 2 * b

# ---- "Wenn ihr was bestellt": question slams in ----
_, e_uns = po("uns"); s_post, _ = po("post")
E.append(El(o(4.58), s_post + 0.02, X0, Y1, slam(make_bar("BESTELLT?", "K", BIG)), enter=(0, 0), dist=0, din=0.06, dout=0.10))

# ---- one yellow statement bar that rolls through the whole explanation ----
_, e_rockt = po("rockt"); s_var, _ = po("var"); _, e_pieces = po("pieces"); s_karu, _ = po("karu")
t_pf = o(7.98)
roll = [(0, "POSTET FITPICS"), (s_var - t_pf, "EURE VARIATIONEN"), (o(18.17) - t_pf, "REPOSTEN"), (o(19.21) - t_pf, "VERBREITEN"),
        (o(20.69) - t_pf, "AUF DER WEBSITE"), (o(23.63) - t_pf, "GANZ UNTEN"), (o(24.37) - t_pf, "KARUSSELL"),
        (o(26.89) - t_pf, "ALLE KUNDEN"), (o(28.27) - t_pf, "DIE LAVISH ROCKEN")]
E.append(El(t_pf, e_rockt, X0, Y1, rolling_bar(roll, "Y", BIG), enter=(0, 0), dist=0, din=0.06, do_sweep=True))
SHAKE += [(t_pf + 0.02, 0.18, 8), (o(24.37) + 0.02, 0.16, 6)]

# ---- "eure Fitpics sehen": customer photos one after another ----
_, e_sehen = po("sehen")
card_seq(["fp1", "fp2", "fp3", "fp4"], o(9.73), e_sehen, X0, RW)

# ---- "verschiedenste Variationen mit den Pieces": the same four as a grid, slammed in one by one ----
GW = 172
for i, p in enumerate(["fp1", "fp3", "fp2", "fp4"]):
    gx = X0 + (i % 2) * (GW + 12); gy = RW + (i // 2) * (int(GW * 1.25) + 12)
    im = Image.open(IMG + p + ".png").convert("RGB"); h = int(GW * 1.25)
    sc = max(GW / im.width, h / im.height); im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    im = im.crop(((im.width - GW) // 2, (im.height - h) // 2, (im.width - GW) // 2 + GW, (im.height - h) // 2 + h))
    tile = Image.new("RGBA", (GW + 12, h + 12), INK + (255,)); tile.paste(im, (6, 6))
    E.append(El(s_var + 0.10 + i * 0.16, e_pieces, gx, gy, slam(tile, dur=0.14), enter=(0, 0), dist=0, din=0.06, drift=(0, 3)))

# ---- "reposten / verbreiten": the Instagram profile ----
popped(IMG + "insta.png", CW, o(18.17), o(20.69), X0, RW)

# ---- "auf meiner Website ... ganz unten ist ein Karussell": the real page, running ----
vc, vw, vh = video_card(J + "/scr", 1.2)
t_web = o(20.69); t_car = o(24.37); t_alle = o(25.91)
E.append(El(t_web, t_alle, X0, RW, vc, enter=(-1, 0), dist=460, din=0.30, drift=(0, 0), dout=0.10))
E.append(El(t_car + 0.06, t_alle, X0 - 4, RW + 8 + 132, static(outline(vw + 8, 226)), enter=(0, 0), dist=0, din=0.10, drift=(0, 0), shadow=False))

# ---- "alle Fitpics von allen Kunden, die Lavish gerockt haben": the customers ----
card_seq(["party1", "party2", "fp3"], t_alle, e_rockt, X0, RW)

# ---- "Also, schickt immer durch": handle to tag ----
t_sd = o(33.25); t_end = o(34.60)
E.append(El(t_sd, t_end, X0, Y1, slam(make_bar("SCHICKT DURCH", "K", BIG)), enter=(0, 0), dist=0, din=0.06, dout=0.12))
SHAKE.append((t_sd + 0.02, 0.16, 7))
E.append(El(o(33.50), t_end, X0, RW, static(make_bar("MARKIERT @LLLAVISHCLO", "Y", MID)), enter=(-1, 0), dist=300, dout=0.12))

# ---------------- hook title (behind the owner) ----------------
HOOK_END = piece_out("hook")[1]
def hook_layer(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sq = 0.80
    grow = 1.0 + 0.03 * min(1, t / HOOK_END)
    for word, size, cy, t0, dt in (("EURE", 260, 430, 0.10, 0.07), ("FITPICS", 250, 680, 0.42, 0.05)):
        f = font(HEAD, size); ws = [f.getlength(c) * sq * grow for c in word]; x = (W - sum(ws)) / 2
        for i, c in enumerate(word):
            ts = t0 + i * dt
            if t >= ts:
                p = min(1, (t - ts) / 0.10); s2 = (1.40 - 0.40 * ease_out(p)) * grow
                ti = Image.new("RGBA", (int(f.getlength(c)) + 12, int(size * 1.22)), (0, 0, 0, 0))
                ImageDraw.Draw(ti).text((6, -int(size * 0.115)), c, font=f, fill=BEI + (255,))
                ti = ti.resize((max(1, int(ti.width * sq * s2)), max(1, int(ti.height * s2))), Image.LANCZOS)
                if p < 1: ti.putalpha(ti.getchannel("A").point(lambda v: int(v * min(1, p * 1.7))))
                layer.alpha_composite(ti, (int(x + ws[i] / 2 - ti.width / 2), int(cy - ti.height / 2)))
            x += ws[i]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (0, 10), layer.getchannel("A").point(lambda v: int(v * 0.50)))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); sh.alpha_composite(layer)
    return sh

# ---------------- grade (footage only, graphics stay clean) ----------------
_x = np.arange(256, dtype=np.float32) / 255
_c = np.where(_x > 0.46, 0.46 + (_x - 0.46) * 0.74, _x)          # pull highlights down, keep shadows and skin
_c = (_c - 0.5) * 1.05 + 0.5
LUT = (_c.clip(0, 1) * 255).astype(np.uint8)
_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
TOPFALL = 0.84 + 0.16 * np.clip(_yy / 0.50, 0, 1) ** 1.5       # natural light fall-off towards the top of the wall
def grade(arr):
    a = cv2.LUT(arr, LUT).astype(np.float32)
    lum = a @ np.float32([0.299, 0.587, 0.114])
    a = lum[..., None] + (a - lum[..., None]) * 0.88
    a *= np.float32([0.985, 1.0, 1.025])
    return (a * TOPFALL).clip(0, 255).astype(np.uint8)

# ---------------- camera (zoom anchored on the head) ----------------
# name: (z_start, z_end, head_src(x, y), head_target(x, y))
R = (1.35, 1.35)   # left frame edge kept: head sits at 1.35 * head_x, graphics column ends at x≈440
CAM = {
 "hook": (1.00, 1.06, (700, 780), (700, 780)),
 "best": R + ((518, 712), (900, 725)), "uns": (1.45, 1.50, (530, 700), (720, 745)),
 "post": R + ((554, 659), (900, 725)), "sehen": R + ((555, 658), (900, 725)),
 "var": R + ((600, 650), (900, 725)), "pieces": R + ((538, 660), (900, 725)),
 "repost": R + ((480, 660), (900, 725)), "karu": R + ((560, 645), (900, 725)),
 "lavish": (1.45, 1.48, (570, 641), (800, 700)), "rockt": R + ((567, 641), (900, 725)),
 "also": (1.45, 1.50, (560, 650), (760, 720)), "out": (1.30, 1.00, (484, 674), (620, 725)),
}
def cam_matrix(name, p):
    z0, z1, (hx, hy), (tx_, ty_) = CAM[name]
    z = z0 + (z1 - z0) * (p * p * (3 - 2 * p))
    tx = min(0.0, max(W - W * z, tx_ - z * hx)); ty = min(0.0, max(H - H * z, ty_ - z * hy))
    return np.float32([[z, 0, tx], [0, z, ty]]), z

# ---------------- run ----------------
ranges = [(round(a * FPS), round(b * FPS), n) for a, b, n in P]
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"),
    output_confidence_masks=True, running_mode=vision.RunningMode.VIDEO))
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", J + "/master.mkv", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", J + "/gfx.mkv"], stdin=subprocess.PIPE)
idx = 0; n_out = 0; ri = 0
while ri < len(ranges):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    f0, f1, name = ranges[ri]
    if idx >= f1:
        ri += 1
        if ri >= len(ranges): break
        f0, f1, name = ranges[ri]
    if idx < f0: idx += 1; continue
    t = n_out / FPS
    arr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    M, z = cam_matrix(name, (idx - f0) / max(1, f1 - f0 - 1))
    for t0_, d_, amp_ in SHAKE:
        if t0_ <= t < t0_ + d_:
            k_ = 1 - (t - t0_) / d_; ph_ = (t - t0_) * 60
            M[0, 2] += amp_ * k_ * np.sin(ph_ * 2.3); M[1, 2] += amp_ * k_ * np.cos(ph_ * 1.7); z = max(z, 1.0011)
    if z > 1.001 or M[0, 2] or M[1, 2]:
        arr = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    arr = grade(arr)
    base = Image.fromarray(arr)
    if t < HOOK_END:
        r = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(arr)), int(t * 1000))
        bg = np.array(r.confidence_masks[0].numpy_view()).reshape(H, W)
        mask = Image.fromarray(((1 - bg) * 255).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2))
        fr = base.convert("RGBA"); fr.alpha_composite(hook_layer(t))
        base = Image.composite(base, fr.convert("RGB"), mask)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); any_el = False
    for el in E:
        if el.t_in <= t < el.t_out: el.draw(layer, t); any_el = True
    if any_el:
        fr = base.convert("RGBA"); fr.alpha_composite(layer); base = fr.convert("RGB")
    enc.stdin.write(np.asarray(base).tobytes()); n_out += 1; idx += 1

# end card: hard cut to black, logo only (owner: "am Ende nur das Logo")
logo = Image.open(LOGO_PNG).convert("RGBA")
for k in range(int(round(LOGO * FPS))):
    p = k / (LOGO * FPS); hgt = int(620 * (1.0 + 0.04 * p))
    lg = logo.resize((int(logo.width * hgt / logo.height), hgt), Image.LANCZOS)
    fr = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    fr.alpha_composite(lg, (int(W / 2 - lg.width / 2), int(860 - lg.height / 2)))
    enc.stdin.write(np.asarray(fr.convert("RGB")).tobytes()); n_out += 1
enc.stdin.close(); enc.wait(); dec.kill()
json.dump({"frames": n_out, "events": [[round(e.t_in, 3), round(e.t_out, 3), e.x, e.y] for e in E], "hook_end": HOOK_END, "total": TOTAL},
          open(J + "/gfx.json", "w"))
print("frames", n_out, "expected", round((TOTAL + LOGO) * FPS))
