"""head position per master frame (face skin + hair centroid), smoothed -> head.json"""
import sys, json, subprocess, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
from scipy.ndimage import gaussian_filter1d
S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"; J = sys.argv[1]
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"), output_confidence_masks=True))
w, h = 360, 640
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", J + "/master.mkv", "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
xs, ys, tops = [], [], []
while True:
    b = dec.stdout.read(w * h * 3)
    if len(b) < w * h * 3: break
    cm = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(b, np.uint8).reshape(h, w, 3).copy())).confidence_masks
    m = (cm[3].numpy_view().reshape(h, w) > 0.5) | (cm[1].numpy_view().reshape(h, w) > 0.5)
    if m.sum() > 30:
        yy, xx = np.nonzero(m); xs.append(xx.mean() * 3); ys.append(yy.mean() * 3); tops.append(np.percentile(yy, 2) * 3)
    else: xs.append(np.nan); ys.append(np.nan); tops.append(np.nan)
out = {}
for k, v in (("x", xs), ("y", ys), ("top", tops)):
    v = np.array(v); ok = ~np.isnan(v); out["valid"] = ok.astype(int).tolist()
    v = np.interp(np.arange(len(v)), np.flatnonzero(ok), v[ok]) if ok.any() else v
    out[k] = gaussian_filter1d(v, 8).round(1).tolist()
json.dump(out, open(J + "/head.json", "w")); print("frames", len(xs), "valid", sum(out["valid"]))
