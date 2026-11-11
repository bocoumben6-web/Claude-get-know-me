import numpy as np, mediapipe as mp, glob, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from mediapipe.tasks.python import vision, BaseOptions

S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
E = S + "/edit"
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"),
    output_confidence_masks=True, running_mode=vision.RunningMode.VIDEO))

F = ImageFont.truetype(S + "/font/rubik900.ttf", 235)
SQ = 0.80                      # horizontal squeeze -> closer to the owner's font
COL = (252, 240, 228, 255)     # #FCF0E4
lines = [("NEUE", 300), ("WEBSITE?", 530)]

letters = []
for text, y in lines:
    ws = [F.getlength(c) * SQ for c in text]
    x = (1080 - sum(ws)) / 2
    for c, w in zip(text, ws):
        letters.append((c, x, y, w))
        x += w

def tile(c):
    bb = F.getbbox(c)
    w = int(F.getlength(c)) + 10
    h = bb[3] + 10
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((5, 0), c, font=F, fill=COL)
    return im.resize((max(1, int(w * SQ)), h), Image.LANCZOS)

tiles = [tile(c) for c, *_ in letters]
T0, DT, POP, END = 0.08, 0.045, 0.10, 2.30

files = sorted(glob.glob(E + "/hc/*.png"))
for i, fc in enumerate(files):
    t = i / 30
    clean = Image.open(fc).convert("RGB")
    orig = Image.open(fc.replace("/hc/", "/hk_o/")).convert("RGB")
    if t < END:
        r = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.array(orig)), int(t * 1000))
        bg = np.array(r.confidence_masks[0].numpy_view()).reshape(1920, 1080).copy()
        bg[950:, :] = 1.0  # person restore only in the headline zone
        mask = Image.fromarray(((1 - bg) * 255).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2))
        layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        for k, ((c, x, y, w), tl) in enumerate(zip(letters, tiles)):
            ts = T0 + k * DT
            if t < ts:
                continue
            p = min(1, (t - ts) / POP)
            e = 1 - (1 - p) ** 3
            s = 1.45 - 0.45 * e
            im = tl.resize((max(1, int(tl.width * s)), max(1, int(tl.height * s))), Image.LANCZOS)
            if p < 1:
                a = min(1, p * 1.6)
                im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
            cx, cy = x + tl.width / 2, y + tl.height / 2
            layer.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
        base = clean.convert("RGBA")
        base.alpha_composite(layer)
        out = Image.composite(orig, base.convert("RGB"), mask)
    else:
        out = clean
    out.save(fc.replace("/hc/", "/hout/"))
print("done", len(files))
sys.stdout.flush()
