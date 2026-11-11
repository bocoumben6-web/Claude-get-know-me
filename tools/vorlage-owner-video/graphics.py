"""Lavish keyword graphics: big callouts behind the owner, checklist, flashback grade.
Reads cut.mkv (after cuts/zooms), writes gfx.mkv (+ sfx.json with whoosh times)."""
import json, subprocess, numpy as np, mediapipe as mp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mediapipe.tasks.python import vision, BaseOptions

S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
E = S + "/edit"
W, H, FPS = 1080, 1920, 30
BEIGE, YELLOW = (252, 240, 228, 255), (240, 204, 56, 255)
BIG = ImageFont.truetype(S + "/font/rubik900.ttf", 230)
LIST = ImageFont.truetype("/home/user/Claude-get-know-me/assets/fonts/BebasNeue-Regular.ttf", 84)
SQ = 0.80

words = json.load(open(E + "/words.json"))
pieces = json.load(open(E + "/pieces.json"))

def wt(word, after):
    for w in words:
        if w["s"] >= after - 0.05 and word.lower() in w["w"].lower():
            return w["s"]
    raise KeyError(word)

def new(t):
    """source time -> time in the cut video"""
    off = 0.0
    for ps, pe, *_ in pieces:
        if ps <= t < pe:
            return off + t - ps
        off += pe - ps
    return off

# ---------- events (source times) ----------
EV = []
def callout(lines, s, e, size=1.0):
    EV.append(dict(kind="big", lines=lines, s=new(s), e=new(e), size=size))
callout(["GRÖSSER"], wt("größer", 3.8), 4.90)
callout(["ANDERES", "LEVEL"], wt("anderes", 5.5), 6.90)
callout(["FIRE"], wt("fire", 10.0), 11.36, 1.25)
callout(["SWAG"], wt("wake", 15.6), 17.22, 1.15)
callout(["BACK IN", "THE DAYS"], wt("back", 17.9), 19.90)
callout(["GANZ", "NACH OBEN"], wt("ganz", 35.5), 36.96)
callout(["SEID", "GESPANNT"], 39.20, 40.21)
LIST_ITEMS = [("x", "KEINE AHNUNG", new(wt("keine", 22.0))),
              ("v", "BESTES VERSUCHT", new(wt("bestes", 25.0))),
              ("v", "SALES GENERIERT", new(wt("sales", 27.0))),
              ("up", "STEIGERUNG", new(wt("ständige", 28.5)))]
LIST_END = new(31.76)
FLASH = (new(17.87), new(21.79))        # flashback grade: "back in the days ... ganz alleine"

# ---------- pre-render ----------
def big_tile(lines, size):
    f = BIG.font_variant(size=int(230 * size))
    lh = int(f.size * 0.95)
    ws = [int(f.getlength(l)) + 20 for l in lines]
    im = Image.new("RGBA", (max(ws), lh * len(lines) + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text(((im.width - ws[i]) / 2 + 10, i * lh), l, font=f, fill=BEIGE)
    im = im.resize((int(im.width * SQ), im.height), Image.LANCZOS)
    if im.width > 940:
        k = 940 / im.width; im = im.resize((940, int(im.height * k)), Image.LANCZOS)
    return im

def icon(kind, r=34):
    im = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = r + 2
    d.ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=YELLOW)
    k = (24, 24, 24, 255)
    if kind == "v":
        d.line([(c - 15, c + 1), (c - 4, c + 12), (c + 16, c - 12)], fill=k, width=8, joint="curve")
    elif kind == "x":
        d.line([(c - 12, c - 12), (c + 12, c + 12)], fill=k, width=8)
        d.line([(c - 12, c + 12), (c + 12, c - 12)], fill=k, width=8)
    else:
        d.polygon([(c, c - 16), (c - 14, c + 2), (c + 14, c + 2)], fill=k)
        d.rectangle((c - 5, c, c + 5, c + 16), fill=k)
    return im

for ev in EV:
    ev["img"] = big_tile(ev["lines"], ev["size"])
list_imgs = []
for kind, text, t in LIST_ITEMS:
    tw = int(LIST.getlength(text)) + 10
    im = Image.new("RGBA", (90 + tw, 100), (0, 0, 0, 0))
    im.alpha_composite(icon(kind), (0, 12))
    d = ImageDraw.Draw(im)
    d.text((94, 2), text, font=LIST, fill=(0, 0, 0, 110))   # soft shadow
    d.text((90, 0), text, font=LIST, fill=BEIGE)
    list_imgs.append((im, t))

def ease(p): return 1 - (1 - p) ** 3

def draw_frame(t):
    """returns list of (tile, x, y, event-or-None); None = always in front"""
    out_l = []
    for ev in EV:
        if ev["s"] <= t < ev["e"]:
            p = min(1, (t - ev["s"]) / 0.13); sc = 1.35 - 0.35 * ease(p)
            fade = max(0, min(1, (ev["e"] - t) / 0.12))
            a = min(1, p * 1.7) * fade
            im = ev["img"].resize((int(ev["img"].width * sc), int(ev["img"].height * sc)), Image.LANCZOS)
            if a < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
            cy = 300 + ev["img"].height / 2
            out_l.append((im, int(W / 2 - im.width / 2), int(cy - im.height / 2), ev))
    if LIST_ITEMS[0][2] <= t < LIST_END:
        fade = max(0, min(1, (LIST_END - t) / 0.15))
        for i, (im, ts) in enumerate(list_imgs):
            if t < ts: continue
            p = min(1, (t - ts) / 0.18); a = ease(p) * fade
            tile = im.copy()
            if a < 1: tile.putalpha(tile.getchannel("A").point(lambda v: int(v * a)))
            out_l.append((tile, int(80 - 50 * (1 - ease(p))), 190 + i * 100, None))
    return out_l

def occluded(ev, mask):
    """share of the final text pixels hidden by the owner"""
    im = ev["img"]; x = int(W / 2 - im.width / 2); y = int(300)
    a = np.array(im.getchannel("A")) > 128
    m = np.array(mask.crop((x, y, x + im.width, y + im.height))) > 128
    return (a & m).sum() / max(1, a.sum())

def flashback(arr, rng):
    g = arr.astype(np.float32)
    gray = g @ np.array([0.299, 0.587, 0.114], np.float32)
    g = 0.1 * g + 0.9 * gray[..., None]
    g = (g - 128) * 1.18 + 122
    g += rng.normal(0, 11, g.shape[:2])[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.35 * (((xx - W / 2) / (W / 1.4)) ** 2 + ((yy - H / 2) / (H / 1.4)) ** 2)
    return np.clip(g * v[..., None], 0, 255).astype(np.uint8)

# ---------- run ----------
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"),
    output_confidence_masks=True, running_mode=vision.RunningMode.VIDEO))
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", E + "/cut.mkv", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", E + "/cut.mkv", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-c:a", "copy", E + "/gfx.mkv"],
                       stdin=subprocess.PIPE)
rng = np.random.default_rng(7); n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = n / FPS
    arr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    items = draw_frame(t)
    mask = None
    if items:
        r = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(arr)), int(t * 1000))
        bg = np.array(r.confidence_masks[0].numpy_view()).reshape(H, W)
        mask = Image.fromarray(((1 - bg) * 255).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2))
        for *_, ev in items:
            if ev is not None and "front" not in ev:
                ev["front"] = occluded(ev, mask) > 0.25
                print("event", ev["lines"], "front" if ev["front"] else "behind")
    if FLASH[0] <= t < FLASH[1]:
        arr = flashback(arr, rng)
    if items:
        behind = Image.new("RGBA", (W, H), (0, 0, 0, 0)); front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for im, x, y, ev in items:
            (front if ev is None or ev["front"] else behind).alpha_composite(im, (x, y))
        base = Image.fromarray(arr)
        fr = base.convert("RGBA"); fr.alpha_composite(behind)
        comp = Image.composite(base, fr.convert("RGB"), mask).convert("RGBA")
        comp.alpha_composite(front)
        arr = np.array(comp.convert("RGB"))
    enc.stdin.write(np.ascontiguousarray(arr).tobytes()); n += 1
enc.stdin.close(); enc.wait()
sfx = [ev["s"] for ev in EV] + [t for *_, t in LIST_ITEMS] + [FLASH[0]]
json.dump(sorted(sfx), open(E + "/sfx.json", "w"))
print("frames", n, "sfx", len(sfx))
