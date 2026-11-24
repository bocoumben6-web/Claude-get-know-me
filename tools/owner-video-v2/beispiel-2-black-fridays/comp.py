"""Lavish owner video, grown-up look + motion.
Clean bars (yellow / black / off-white), slide-in with motion blur + overshoot, living hold (drift),
count-ups, light sweep, text roll (morph in place), camera pushes, hook title behind the owner, QR tile, logo end card.
Reads master.mkv by frame index (exact sync), writes gfx.mkv (video only)."""
import sys, json, subprocess, math, numpy as np, cv2, mediapipe as mp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mediapipe.tasks.python import vision, BaseOptions

S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
J = S + "/job6"
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

# ======================= Video 1: 2 Black Fridays (selfie close-up: graphics live in the lower third) =======================
o = out_time; po = piece_out; END = TOTAL
E = []; SHAKE = []; BOXLOG = {}
BIG, MID, TAG = 96, 70, 46
hb = bar_metrics(BIG)[0]; hm = bar_metrics(MID)[0]; GAP = 10
Y1 = 1222; RW = Y1 + hb + GAP
A4833 = 17.40; A4834 = 29.367

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
def slam(im, dur=0.16): return pop_card(im, k0=1.45, dur=dur)
def struck_bar(text, style, size, t_strike, dur=0.24):
    base = make_bar(text, style, size); h = base.height
    def content(tl):
        im = slam(base)(tl)
        p = ease_out((tl - t_strike) / dur)
        if p > 0:
            d = ImageDraw.Draw(im); x1 = int(16 + (im.width - 32) * p); th = max(8, h // 9); y = h // 2 - th // 2
            d.rectangle((16, y, x1, y + th), fill=(INK if style == "Y" else YEL) + (255,))
        return im
    return content
def q_card(n, w=104, h=136, dur=0.26):
    f = font(HEAD, 96); fs = font(BEBAS, 30)
    card = Image.new("RGBA", (w, h), INK + (255,)); d = ImageDraw.Draw(card)
    d.rectangle((0, 0, w - 1, h - 1), outline=YEL + (255,), width=4)
    qw = f.getlength("?"); d.text(((w - qw) / 2, 2), "?", font=f, fill=BEI + (255,))
    lab = f"0{n}"; d.text(((w - fs.getlength(lab)) / 2, h - 38), lab, font=fs, fill=YEL + (255,))
    def content(tl):
        p = ease_back(tl / dur, 1.6)
        sx = max(0.02, min(1.12, p)); im = card.resize((max(2, int(w * sx)), h), Image.LANCZOS)
        cv = Image.new("RGBA", (int(w * 1.12) + 2, h), (0, 0, 0, 0)); cv.alpha_composite(im, ((cv.width - im.width) // 2, 0))
        return cv
    return content

# ---- first "hier" = the job, second "hier" = Lavish ----
t_h1 = o(A4833 + 1.62); t_h2 = o(A4833 + 3.92); e_hier = po("tough")[0] + 0.42   # Lavish part stays over the cut until ECHT TOUGH
E.append(El(t_h1, e_hier, X0, Y1, rolling_bar([(0, "BLACK FRIDAY 1"), (t_h2 - t_h1, "BLACK FRIDAY 2")], "Y", BIG),
            enter=(0, 0), dist=0, din=0.06, do_sweep=True, cut_out=True))
SHAKE += [(t_h1 + 0.02, 0.16, 7), (t_h2 + 0.02, 0.14, 5)]
E.append(El(t_h1 + 0.22, e_hier, X0, RW, rolling_bar([(0, "IM JOB"), (t_h2 - t_h1 - 0.22, "BEI LAVISH")], "K", MID),
            enter=(-1, 0), dist=300, cut_out=True))
# three secret cards (open loop, revealed at the end)
w_lav = make_bar("BEI LAVISH", "K", MID).width
for i in range(3):
    E.append(El(t_h2 + 0.12 + i * 0.12, e_hier, X0 + w_lav + 24 + i * 124, RW - 28, q_card(i + 1), enter=(0, 0), dist=0, din=0.06, drift=(0, 2), cut_out=True))

# ---- "Das ist echt tough" ----
s_t, e_t = po("tough")
E.append(El(s_t + 0.45, e_t, X0, Y1, slam(make_bar("ECHT TOUGH", "K", BIG)), enter=(0, 0), dist=0, din=0.06, cut_out=True))
SHAKE.append((s_t + 0.47, 0.18, 8))

# ---- "Ich würde auch nur einen Black Friday machen, aber so ist es noch nicht" ----
s_n, _ = po("nur1"); s_nn, e_nn = po("nicht")
t_strike = o(A4834 + 7.24) - s_n
E.append(El(s_n + 0.12, e_nn, X0, Y1, struck_bar("NUR 1 BLACK FRIDAY", "Y", BIG, t_strike), enter=(0, 0), dist=0, din=0.06, cut_out=True))
E.append(El(o(A4834 + 7.24) + 0.12, e_nn, X0, RW, static(make_bar("NOCH NICHT", "K", MID)), enter=(-1, 0), dist=300, cut_out=True))

# ---- reveal: the three beanies (cut-away board over the blurred showroom) ----
s_b, e_b = po("boy")
BEANIES = [S + "/batch/img/beanie_" + c + ".png" for c in ("white", "black", "camo")]
BW = 330
def beanie(path):
    im = Image.open(path).convert("RGBA"); im = im.crop(im.getchannel("A").getbbox())
    return im.resize((BW, int(BW * im.height / im.width)), Image.LANCZOS)
BI = [beanie(p) for p in BEANIES]; BH = BI[0].height
BX = [24 + i * (BW + 9) for i in range(3)]; BY = 560
for i in range(3):
    E.append(El(s_b + 0.05 + i * 0.22, END, BX[i], BY, slam(BI[i], dur=0.18), enter=(0, 0), dist=0, din=0.06, drift=(0, 3), cut_out=True))
    num = make_bar(f"0{i+1}", "Y", TAG)
    E.append(El(s_b + 0.15 + i * 0.22, END, BX[i] + (BW - num.width) // 2, BY + BH + 18, static(num), enter=(0, 1), dist=80, din=0.2, drift=(0, 0), cut_out=True, shadow=False))
t_q = s_b + 0.95
E.append(El(t_q, END, X0, 330, slam(make_bar("WELCHE NIMMST DU?", "K", BIG)), enter=(0, 0), dist=0, din=0.06, cut_out=True))
E.append(El(s_b + 1.72, END, X0, Y1, static(make_bar("SCHREIB 1 2 ODER 3", "Y", MID)), enter=(-1, 0), dist=300, cut_out=True))
SHAKE.append((s_b + 0.01, 0.14, 6))
CUTAWAY = (s_b, e_b)

# ---------------- hook headline (front, lower third; the close-up leaves no room behind the head) ----------------
HOOK_END = po("hook")[1]; T_ZWEI = o(8.86)
def hook_layer(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sq = 0.84
    for word, size, cy, t0, dt in (("BLACK FRIDAY", 112, 1400, 0.06, 0.045), ("2X", 150, 1285, T_ZWEI, 0.06)):
        f = font(HEAD, size); ws = [f.getlength(c) * sq for c in word]; x = (W - sum(ws)) / 2
        for i, c in enumerate(word):
            ts = t0 + i * dt
            if t >= ts and c != " ":
                p = min(1, (t - ts) / 0.10); s2 = 1.40 - 0.40 * ease_out(p)
                ti = Image.new("RGBA", (int(f.getlength(c)) + 12, int(size * 1.22)), (0, 0, 0, 0))
                ImageDraw.Draw(ti).text((6, -int(size * 0.115)), c, font=f, fill=(YEL if word == "2X" else BEI) + (255,))
                ti = ti.resize((max(1, int(ti.width * sq * s2)), max(1, int(ti.height * s2))), Image.LANCZOS)
                if p < 1: ti.putalpha(ti.getchannel("A").point(lambda v: int(v * min(1, p * 1.7))))
                layer.alpha_composite(ti, (int(x + ws[i] / 2 - ti.width / 2), int(cy - ti.height / 2)))
            x += ws[i]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (0, 10), layer.getchannel("A").point(lambda v: int(v * 0.60)))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); sh.alpha_composite(layer)
    return sh
SHAKE.append((T_ZWEI + 0.02, 0.18, 9))

# ---------------- grade ----------------
_x = np.arange(256, dtype=np.float32) / 255
_c = np.where(_x > 0.46, 0.46 + (_x - 0.46) * 0.74, _x)
_c = (_c - 0.5) * 1.05 + 0.5
LUT = (_c.clip(0, 1) * 255).astype(np.uint8)
_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
TOPFALL = 0.86 + 0.14 * np.clip(_yy / 0.45, 0, 1) ** 1.5
def grade(arr):
    a = cv2.LUT(arr, LUT).astype(np.float32)
    lum = a @ np.float32([0.299, 0.587, 0.114])
    a = lum[..., None] + (a - lum[..., None]) * 0.84          # showroom light is warm: a bit more desaturation
    a *= np.float32([0.975, 1.0, 1.04])
    return (a * TOPFALL).clip(0, 255).astype(np.uint8)

# ---------------- camera: gentle pushes on the face (face is centred in the master) ----------------
FACE = (540, 560)
CAM = {"hook": (1.00, 1.06), "hier": (1.00, 1.05), "tough": (1.10, 1.14), "nur1": (1.00, 1.03), "nicht": (1.03, 1.05), "boy": (1.0, 1.0)}
def cam_matrix(name, p):
    z0, z1 = CAM[name]; z = z0 + (z1 - z0) * (p * p * (3 - 2 * p))
    tx = min(0.0, max(W - W * z, FACE[0] - z * FACE[0])); ty = min(0.0, max(H - H * z, FACE[1] - z * FACE[1]))
    return np.float32([[z, 0, tx], [0, z, ty]]), z

# ---------------- run ----------------
ranges = [(round(a * FPS), round(b * FPS), n) for a, b, n in P]
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", J + "/gfx.mkv"], stdin=subprocess.PIPE)
cap = cv2.VideoCapture(J + "/master.mkv")
def read_frame(i):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read()
    return f[..., ::-1].copy()
n_out = 0
for f0, f1, name in ranges:
    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    for idx in range(f0, f1):
        ok, fbgr = cap.read(); arr = fbgr[..., ::-1].copy()
        t = n_out / FPS
        M, z = cam_matrix(name, (idx - f0) / max(1, f1 - f0 - 1))
        for t0_, d_, amp_ in SHAKE:
            if t0_ <= t < t0_ + d_:
                k_ = 1 - (t - t0_) / d_; ph_ = (t - t0_) * 60
                M[0, 2] += amp_ * k_ * np.sin(ph_ * 2.3); M[1, 2] += amp_ * k_ * np.cos(ph_ * 1.7); z = max(z, 1.0011)
        if CUTAWAY[0] <= t < CUTAWAY[1]:
            arr = cv2.GaussianBlur(cv2.resize(arr, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 6)
            arr = cv2.resize(arr, (W, H), interpolation=cv2.INTER_LINEAR)
            arr = grade(arr); arr = (arr.astype(np.float32) * 0.42).astype(np.uint8)
        else:
            if z > 1.001 or M[0, 2] or M[1, 2]:
                arr = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            arr = grade(arr)
        base = Image.fromarray(arr).convert("RGBA")
        boxes = []
        if t < HOOK_END:
            hl = hook_layer(t); base.alpha_composite(hl); bb = hl.getbbox()
            if bb: boxes.append(list(bb))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for el in E:
            if el.t_in <= t < el.t_out:
                el.draw(layer, t); im = el.content(t - el.t_in); boxes.append([el.x, el.y, el.x + im.width, el.y + im.height])
        base.alpha_composite(layer)
        if n_out % 10 == 0: BOXLOG[n_out] = boxes
        enc.stdin.write(np.asarray(base.convert("RGB")).tobytes()); n_out += 1

# end card: logo only, short (retention rule: max 0.8 s)
logo = Image.open(LOGO_PNG).convert("RGBA")
for k in range(int(round(LOGO * FPS))):
    p = k / (LOGO * FPS); hgt = int(620 * (1.0 + 0.04 * p))
    lg = logo.resize((int(logo.width * hgt / logo.height), hgt), Image.LANCZOS)
    fr = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    fr.alpha_composite(lg, (int(W / 2 - lg.width / 2), int(860 - lg.height / 2)))
    enc.stdin.write(np.asarray(fr.convert("RGB")).tobytes()); n_out += 1
enc.stdin.close(); enc.wait()
json.dump({"frames": n_out, "events": [[round(e.t_in, 3), round(e.t_out, 3), e.x, e.y] for e in E], "hook_end": HOOK_END, "total": TOTAL,
           "boxes10": BOXLOG, "skip_face": [list(CUTAWAY)]}, open(J + "/gfx.json", "w"))
print("frames", n_out, "expected", round((TOTAL + LOGO) * FPS))
