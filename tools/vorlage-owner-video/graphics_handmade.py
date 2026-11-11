"""Lavish v3: handmade look. Tape labels, torn paper, worn stamp word, photocopy freeze, camcorder flashback.
Reads cut3.mkv, writes gfx3.mkv. No icons, no UI cards, no uniform pop animations."""
import json, subprocess, numpy as np, mediapipe as mp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mediapipe.tasks.python import vision, BaseOptions

S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
E = S + "/edit"
W, H, FPS = 1080, 1920, 30
BEIGE, YELLOW, INK = (252, 240, 228), (240, 204, 56), (22, 22, 22)
BEBAS = "/home/user/Claude-get-know-me/assets/fonts/BebasNeue-Regular.ttf"
RUBIK = S + "/font/rubik900.ttf"
rng = np.random.default_rng(11)

words = json.load(open(E + "/words.json"))
pieces = json.load(open(E + "/pieces3.json"))

def wt(word, after):
    for w in words:
        if w["s"] >= after - 0.05 and word.lower() in w["w"].lower():
            return w["s"]
    raise KeyError(word)

def new(t):
    off = 0.0
    for ps, pe, *_ in pieces:
        if ps <= t < pe:
            return off + t - ps
        off += pe - ps
    return off

def piece_span(key):
    off = 0.0
    for ps, pe, z, s, e, txt in pieces:
        if key in txt.replace("*", ""):
            return off, off + pe - ps
        off += pe - ps
    raise KeyError(key)

# ---------- handmade elements ----------
def noise_img(w, h, lo, hi, blur=0):
    a = rng.uniform(lo, hi, (h, w))
    im = Image.fromarray(a.clip(0, 255).astype("uint8"))
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im

def rough_mask(w, h, jag=7, ends_only=False):
    """rectangle alpha with torn / cut edges"""
    m = np.full((h, w), 255, np.uint8)
    l = np.clip(np.cumsum(rng.normal(0, 1.3, h)) + jag, 0, 2 * jag).astype(int)
    r = np.clip(np.cumsum(rng.normal(0, 1.3, h)) + jag, 0, 2 * jag).astype(int)
    for y in range(h):
        m[y, :l[y]] = 0; m[y, w - r[y]:] = 0
    if not ends_only:
        t = np.clip(np.cumsum(rng.normal(0, 0.9, w)) + jag / 2, 0, jag).astype(int)
        b = np.clip(np.cumsum(rng.normal(0, 0.9, w)) + jag / 2, 0, jag).astype(int)
        for x in range(w):
            m[:t[x], x] = 0; m[h - b[x]:, x] = 0
    return Image.fromarray(m)

def worn(alpha, amount=0.10):
    """photocopy wear: knock small holes into an alpha channel"""
    n = np.array(noise_img(alpha.width, alpha.height, 0, 255, 1.1))
    thr = np.quantile(n, amount)
    a = np.array(alpha).astype(np.float32)
    a[n < thr] *= 0.15
    return Image.fromarray(a.astype("uint8"))

def with_shadow(im, off=(7, 9), blur=7, strength=120):
    pad = 30
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * strength / 255))
    sh.paste((0, 0, 0, 255), (pad + off[0], pad + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad))
    return out

def label(text, size, kind, rot):
    f = ImageFont.truetype(BEBAS, size)
    tw = int(f.getlength(text)); th = int(size * 0.80)
    padx, pady = int(size * 0.42), int(size * 0.20)
    w, h = tw + 2 * padx, th + 2 * pady
    if kind == "tape":       # yellow gaffer tape, cut ends
        base = np.array(noise_img(w, h, 232, 255, 0)).astype(np.float32) / 255
        streak = np.array(noise_img(w, 1, 0.90, 1.0, 0).resize((w, h))).astype(np.float32) / 255 if False else 1
        col = np.stack([base * YELLOW[0], base * YELLOW[1], base * YELLOW[2]], -1)
        fibres = rng.uniform(0.93, 1.0, (h, 1, 1))
        im = Image.fromarray((col * fibres * streak).clip(0, 255).astype("uint8")).convert("RGBA")
        im.putalpha(rough_mask(w, h, jag=9, ends_only=True).point(lambda v: int(v * 0.96)))
    else:                    # torn photocopy paper
        g = np.array(noise_img(w, h, 214, 246, 0.6)).astype(np.float32)
        im = Image.fromarray(np.stack([g, g * 0.985, g * 0.95], -1).clip(0, 255).astype("uint8")).convert("RGBA")
        im.putalpha(rough_mask(w, h, jag=8))
    txt = Image.new("L", (w, h), 0)
    ImageDraw.Draw(txt).text((padx, pady - int(size * 0.07)), text, font=f, fill=255)
    txt = worn(txt, 0.07 if kind == "tape" else 0.13)
    ink = Image.new("RGBA", (w, h), INK + (0,)); ink.putalpha(txt)
    im.alpha_composite(ink)
    return with_shadow(im).rotate(rot, resample=Image.BICUBIC, expand=True)

def stamp(text, size, color, rot, squeeze=0.80, wear=0.16):
    f = ImageFont.truetype(RUBIK, size)
    w = int(f.getlength(text)) + 40; h = int(size * 1.1)
    a = Image.new("L", (w, h), 0)
    ImageDraw.Draw(a).text((20, -int(size * 0.08)), text, font=f, fill=255)
    a = worn(a, wear)
    im = Image.new("RGBA", (w, h), color + (0,)); im.putalpha(a)
    im = im.resize((int(w * squeeze), h), Image.LANCZOS)
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)

# ---------- events (irregular on purpose) ----------
EV = []
def ev(img, x, y, s, e, behind=False, slap=True):
    EV.append(dict(img=img, x=x, y=y, s=s, e=e, behind=behind, slap=slap))

# 1) yellow tape, top left, crooked
ev(label("ANDERES LEVEL", 104, "tape", 5), 30, 285, new(wt("anderes", 5.5)), new(6.90))
# 2) worn stamp word, huge, cut off at the frame edge, behind the owner
f_s, f_e = piece_span("FIRE")
ev(stamp("FIRE", 560, BEIGE, -6), -70, 150, new(wt("fire", 10.0)), f_e, behind=True)
# 3) photocopy freeze frame on SWAG (handled in the loop) + yellow stamp over it
sw_s, sw_e = piece_span("SWAG")
FREEZE = (sw_e - 0.50, sw_e)
ev(stamp("SWAG", 400, YELLOW, 7, wear=0.12), 110, 620, FREEZE[0], FREEZE[1], slap=False)
# 4) camcorder flashback (handled in the loop), small date stamp only
FLASH = (new(17.87), new(21.79))
# 5) torn paper snippet, right side
ev(label("SALES", 150, "paper", -4), 640, 330, new(wt("sales", 27.0)), new(28.48))
# 6) three scraps climbing upward, each different
g, n_, o = new(wt("ganz", 35.9)), new(wt("noch", 36.2)), new(wt("oben", 36.4))
end6 = piece_span("GANZ NACH OBEN")[1]
ev(label("GANZ", 120, "paper", 4), 60, 560, g, end6)
ev(label("NACH", 120, "tape", -6), 150, 390, n_, end6)
ev(label("OBEN", 170, "paper", 3), 240, 170, o, end6)

DATE = ImageFont.truetype(BEBAS, 58)

def camcorder(arr, t):
    g = arr.astype(np.float32)
    out = g.copy()
    out[:, :-4, 0] = g[:, 4:, 0]           # chroma shift
    out[:, 4:, 2] = g[:, :-4, 2]
    gray = out @ np.array([0.299, 0.587, 0.114], np.float32)
    out = 0.55 * out + 0.45 * gray[..., None]
    out = (out - 128) * 0.92 + 134          # milky blacks
    out[..., 2] *= 1.05; out[..., 0] *= 0.98
    out[::3] *= 0.90                        # scan lines
    out += rng.normal(0, 9, (H, W))[..., None]
    band = int((t * 310) % (H + 200)) - 100 # one slow tracking band
    if 0 <= band < H - 14:
        out[band:band + 14] = np.roll(out[band:band + 14], 14, axis=1) * 1.08
    im = Image.fromarray(out.clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.9))
    d = ImageDraw.Draw(im)
    d.text((72, 1560), "2024", font=DATE, fill=(236, 190, 70))
    return np.array(im)

def photocopy(arr):
    gray = arr.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    g = 255 * (gray / 255) ** 0.62          # lift shadows so faces keep detail
    g = (g - 128) * 1.55 + 128
    g += rng.normal(0, 16, g.shape)
    g = g.clip(0, 255)
    return np.stack([g, g * 0.985, g * 0.95], -1).astype("uint8")

# ---------- run ----------
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"),
    output_confidence_masks=True, running_mode=vision.RunningMode.VIDEO))
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", E + "/cut3.mkv", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", E + "/cut3.mkv", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-c:a", "copy", E + "/gfx3.mkv"],
                       stdin=subprocess.PIPE)
n = 0; frozen = None
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = n / FPS
    arr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    live = [e for e in EV if e["s"] <= t < e["e"]]
    mask = None
    if any(e["behind"] for e in live):
        r = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(arr)), int(t * 1000))
        bg = np.array(r.confidence_masks[0].numpy_view()).reshape(H, W)
        mask = Image.fromarray(((1 - bg) * 255).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2))
    if FREEZE[0] <= t < FREEZE[1]:
        if frozen is None: frozen = photocopy(arr)
        arr = frozen
    elif FLASH[0] <= t < FLASH[1]:
        arr = camcorder(arr, t)
    if live:
        base = Image.fromarray(arr)
        back = base.convert("RGBA"); front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for e in live:
            im, x, y = e["img"], e["x"], e["y"]
            k = int(round((t - e["s"]) * FPS))
            if e["slap"] and k < 2:          # slapped on: 2 frames slightly off, then it sits
                im = im.rotate((2.5, -1.2)[k], resample=Image.BICUBIC, expand=True)
                x += (14, -5)[k]; y += (-10, 4)[k]
            (back if e["behind"] else front).alpha_composite(im, (x, y))
        comp = back.convert("RGB")
        if mask is not None:
            comp = Image.composite(base, comp, mask)
        comp = comp.convert("RGBA"); comp.alpha_composite(front)
        arr = np.array(comp.convert("RGB"))
    enc.stdin.write(np.ascontiguousarray(arr).tobytes()); n += 1
enc.stdin.close(); enc.wait()
json.dump([[round(e["s"], 2), round(e["e"], 2)] for e in EV] + [list(FLASH)], open(E + "/ev3.json", "w"))
print("frames", n)
