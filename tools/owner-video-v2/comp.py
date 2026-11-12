"""Lavish owner video, grown-up look + motion.
Clean bars (yellow / black / off-white), slide-in with motion blur + overshoot, living hold (drift),
count-ups, light sweep, text roll (morph in place), camera pushes, hook title behind the owner, QR tile, logo end card.
Reads master.mkv by frame index (exact sync), writes gfx.mkv (video only)."""
import sys, json, subprocess, math, numpy as np, cv2, mediapipe as mp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mediapipe.tasks.python import vision, BaseOptions

S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
J = S + "/job2"
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
BIG, MID = 96, 70                       # hierarchy: one big statement bar, smaller rows under it
hb = bar_metrics(BIG)[0]; hm = bar_metrics(MID)[0]; GAP = 12
Y1 = 300; RW = Y1 + hb + GAP

# ---- website: big bar + the real homepage screenshot ----
t_site, t_bar, t_link, t_grp = o(8.60), o(10.86), o(12.95), o(13.74)
E.append(El(t_site, t_bar - 0.02, X0, Y1, static(make_bar("NEUE WEBSITE", "K", BIG)), enter=(-1, 0), do_sweep=True))
cw = framed(J + "/card_web.png", 300); sw = framed(J + "/strip_web.png", 700, b=6)
t_card = o(8.74); SHIFT = sw.height + GAP
E.append(El(t_card, t_grp + 0.22, X0, RW, static(cw), enter=(-1, 0), dist=440, din=0.32, drift=(0, 0),
            move=lambda tl: (0, SHIFT * ease_out((tl - (t_link - t_card)) / 0.28))))
# "oben steht direkt ...": yellow frame marks the banner at the top of the page
E.append(El(t_bar + 0.14, t_link + 0.04, X0 - 5, RW - 5, static(outline(cw.width + 10, 8 + int(111 * 300 / 1206) + 12)), enter=(0, 0), dist=0,
            din=0.12, dout=0.06, drift=(0, 0), shadow=False))
# "... der WhatsApp-Link": the banner jumps out of the page, big and readable; the page slides down under it
def strip_pop(tl):
    k = 300 / 700 + (1 - 300 / 700) * ease_back(tl / 0.30, 1.6)
    return sw.resize((max(2, int(sw.width * k)), max(2, int(sw.height * k))), Image.LANCZOS)
E.append(El(t_link, t_grp + 0.14, X0, RW, strip_pop, enter=(0, 0), dist=0, din=0.10, drift=(0, 0)))
# one yellow bar that drops from the top and rolls through three states; benefits stack under it
STACK_END = o(18.90)
E.append(El(t_bar, STACK_END, X0, Y1, rolling_bar([(0, "DIREKT OBEN"), (t_link - t_bar, "WHATSAPP-LINK"),
            (t_grp - t_bar, "WHATSAPP-GRUPPE")], "Y", BIG), enter=(0, -1), dist=320, do_sweep=True))
R1 = RW; R2 = R1 + hm + GAP; R3 = R2 + hm + GAP
E.append(El(o(15.42), STACK_END - 0.03, X0, R1, count_bar(None, 15, "% DISCOUNT", "K", MID), enter=(-1, 0)))
E.append(El(o(16.18), STACK_END - 0.06, X0, R2, static(make_bar("EARLY ACCESS", "W", MID)), enter=(-1, 0)))
E.append(El(o(17.82), STACK_END - 0.09, X0, R3, static(make_bar("SAMPLE REVIEW", "K", MID)), enter=(-1, 0), do_sweep=True))

# ---- pop-up: counter runs to 10, then the real pop-up jumps in ----
_, e_same = piece_out("same")
t_tm = o(20.16); t10 = o(20.56) + 0.62
E.append(El(t_tm, t10 + 0.17, X0, Y1, timer_block(o(20.56) - t_tm, dur=0.60), enter=(-1, 0)))
cp = framed(J + "/card_popup.png", 300); YC = Y1 + hm + GAP
def popup_pop(tl):
    k = 0.80 + 0.20 * ease_back(tl / 0.28, 2.2)
    im = cp.resize((int(cp.width * k), int(cp.height * k)), Image.LANCZOS)
    cv = Image.new("RGBA", cp.size, (0, 0, 0, 0)); cv.alpha_composite(im, ((cp.width - im.width) // 2, (cp.height - im.height) // 2)) if k <= 1 else cv.paste(im.crop(((im.width - cp.width) // 2, (im.height - cp.height) // 2, (im.width - cp.width) // 2 + cp.width, (im.height - cp.height) // 2 + cp.height)))
    return cv
E.append(El(t10 + 0.04, e_same - 0.03, X0, YC, popup_pop, enter=(0, 0), dist=0, din=0.10, drift=(0, 4)))
E.append(El(t10, e_same, X0, Y1, rolling_bar([(0, "NACH 10 SEKUNDEN"), (o(22.47) - t10, "15% + EARLY ACCESS")], "Y", MID),
            enter=(0, -1), dist=260, do_sweep=True))
# "genau dieselbe Geschichte": yellow frame on the WhatsApp button of the pop-up
bx0, by0, bx1, by1 = [int(round(v * 300 / 1110)) for v in (105, 1661, 1004, 1792)]
E.append(El(o(22.47) + 0.12, e_same - 0.03, X0 + 8 + bx0 - 6, YC + 8 + by0 - 6, static(outline(bx1 - bx0 + 12, by1 - by0 + 12)), enter=(0, 0), dist=0,
            din=0.12, drift=(0, 4), shadow=False))

# ---- every new drop: giveaways, discounts, everything else ----
_, e_all = piece_out("alles")
D1 = Y1 + hm + GAP; D2 = D1 + hb + GAP; D3 = D2 + hb + GAP
E.append(El(o(24.66), e_all, X0, Y1, static(make_bar("BEI JEDEM DROP", "W", MID)), enter=(0, -1), dist=260))
E.append(El(o(26.60), e_all - 0.03, X0, D1, static(make_bar("VERLOSUNGEN", "Y", BIG)), enter=(-1, 0), do_sweep=True))
E.append(El(o(29.07), e_all - 0.06, X0, D2, static(make_bar("DISCOUNTS", "K", BIG)), enter=(-1, 0)))
E.append(El(o(30.37), e_all - 0.09, X0, D3, static(make_bar("+ ALLES ANDERE", "W", MID)), enter=(-1, 0)))

# ---- join: one rolling bar above the QR tile; both stay until the logo card (hard cut) ----
END = TOTAL
qt = qr_tile(360)
t_j = o(31.88)
E.append(El(t_j, END, X0, Y1, rolling_bar([(0, "WHATSAPP-GRUPPE"), (o(33.60) - t_j, "HOUSE OF LAVISH")], "Y", MID),
            enter=(0, -1), dist=260, cut_out=True, do_sweep=True, drift=(0, 0)))
E.append(El(o(31.96), END, X0, Y1 + hm + GAP, static(qt), enter=(-1, 0), dist=440, din=0.32, cut_out=True, drift=(0, 0)))

# ---------------- hook title (behind the owner) ----------------
HOOK_END = piece_out("hook2")[1]
def hook_layer(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sq = 0.80
    n = int(round(15 * ease_out(t / 0.55)))
    f = font(HEAD, 400)
    txt = f"{n}%"; ref = "15%"
    wref = int(f.getlength(ref)); im = Image.new("RGBA", (wref + 40, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.text((20 + wref - f.getlength(txt), -40), txt, font=f, fill=BEI + (255,))
    im = im.resize((int(im.width * sq), im.height), Image.LANCZOS)
    bump = 1.0 + 0.10 * max(0.0, 1 - abs(t - 0.58) / 0.14) if 0.44 < t < 0.72 else 1.0
    sc = (1.0 + 0.03 * min(1, t / HOOK_END)) * bump
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    layer.alpha_composite(im, (int(W / 2 - im.width / 2), int(455 - im.height / 2)))
    # second line: letters pop in one by one (the owner's own title animation)
    f2 = font(HEAD, 190); word = "DISCOUNT?"
    ws = [f2.getlength(c) * sq for c in word]; x = (W - sum(ws)) / 2
    for i, c in enumerate(word):
        ts = 0.50 + i * 0.04
        if t >= ts:
            p = min(1, (t - ts) / 0.10); s2 = 1.40 - 0.40 * ease_out(p)
            ti = Image.new("RGBA", (int(f2.getlength(c)) + 12, 230), (0, 0, 0, 0))
            ImageDraw.Draw(ti).text((6, -22), c, font=f2, fill=BEI + (255,))
            ti = ti.resize((max(1, int(ti.width * sq * s2)), max(1, int(ti.height * s2))), Image.LANCZOS)
            if p < 1: ti.putalpha(ti.getchannel("A").point(lambda v: int(v * min(1, p * 1.7))))
            layer.alpha_composite(ti, (int(x + ws[i] / 2 - ti.width / 2), int(735 - ti.height / 2)))
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
CAM = {
 "hook1": (1.00, 1.00, (500, 750), (500, 750)), "hook2": (1.00, 1.00, (462, 680), (462, 680)),
 "erklaer": (1.16, 1.34, (540, 735), (540, 720)),
 "website": (1.18, 1.18, (510, 725), (650, 725)), "walink": (1.18, 1.18, (524, 728), (650, 725)),
 "early": (1.18, 1.18, (570, 718), (660, 725)),
 "sample": (1.18, 1.23, (545, 716), (655, 725)), "same": (1.23, 1.26, (496, 723), (650, 725)),
 "drop": (1.18, 1.20, (523, 720), (650, 725)), "drop2": (1.30, 1.30, (523, 716), (660, 730)),
 "disc": (1.18, 1.18, (533, 711), (650, 725)), "alles": (1.26, 1.26, (513, 718), (655, 728)),
 "join": (1.18, 1.21, (515, 714), (655, 725)),
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

# end card: hard cut to black; logo is the main element, QR + channel name under it
logo = Image.open(LOGO_PNG).convert("RGBA")
qe = qr_tile(380); be = make_bar("HOUSE OF LAVISH", "Y", MID)
for k in range(int(round(LOGO * FPS))):
    p = k / (LOGO * FPS); hgt = int(480 * (1.0 + 0.04 * p))
    lg = logo.resize((int(logo.width * hgt / logo.height), hgt), Image.LANCZOS)
    fr = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    fr.alpha_composite(lg, (int(W / 2 - lg.width / 2), int(560 - lg.height / 2)))
    fr.alpha_composite(be, (int(W / 2 - be.width / 2), 880))
    fr.alpha_composite(qe, (int(W / 2 - qe.width / 2), 880 + be.height + GAP))
    enc.stdin.write(np.asarray(fr.convert("RGB")).tobytes()); n_out += 1
enc.stdin.close(); enc.wait(); dec.kill()
json.dump({"frames": n_out, "events": [[round(e.t_in, 3), round(e.t_out, 3), e.x, e.y] for e in E], "hook_end": HOOK_END, "total": TOTAL},
          open(J + "/gfx.json", "w"))
print("frames", n_out, "expected", round((TOTAL + LOGO) * FPS))
