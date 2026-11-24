"""Landscape 4K selfie clips -> 1080x1920 master that follows the owner's face (smoothed), clips concatenated."""
import sys, subprocess, json, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
from scipy.ndimage import gaussian_filter1d
S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
J = S + "/job6"; SRC = S + "/batch/src/"
CLIPS = sys.argv[1].split(",")
SW, SH, W, H = 3840, 2160, 1080, 1920; CW = round(SH * 9 / 16)   # 1215
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"), output_confidence_masks=True))
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", J + "/t/master_v.mkv"], stdin=subprocess.PIPE)
info = {}; off = 0.0
for c in CLIPS:
    # pass 1: face x (face-skin class) on small frames
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC + c + ".MOV", "-vf", "scale=640:360", "-r", "30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    xs = []
    while True:
        b = dec.stdout.read(640 * 360 * 3)
        if len(b) < 640 * 360 * 3: break
        r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(b, np.uint8).reshape(360, 640, 3).copy()))
        m = r.confidence_masks[3].numpy_view().reshape(360, 640) + r.confidence_masks[1].numpy_view().reshape(360, 640)
        col = (m > 0.5).sum(0).astype(float)
        xs.append(np.average(np.arange(640), weights=col) * SW / 640 if col.sum() > 200 else np.nan)
    xs = np.array(xs); ok = ~np.isnan(xs)
    xs = np.interp(np.arange(len(xs)), np.flatnonzero(ok), xs[ok])
    xsm = gaussian_filter1d(xs, 12)          # ~0.4 s smoothing: calm, but follows
    left = np.clip(xsm - CW / 2, 0, SW - CW)
    # pass 2: crop full-res
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC + c + ".MOV", "-r", "30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = 0
    while True:
        b = dec.stdout.read(SW * SH * 3)
        if len(b) < SW * SH * 3: break
        a = np.frombuffer(b, np.uint8).reshape(SH, SW, 3)
        l = left[min(n, len(left) - 1)]; li = int(l); fr = l - li
        crop = a[:, li:li + CW + 1].astype(np.float32)
        crop = crop[:, :CW] * (1 - fr) + crop[:, 1:CW + 1] * fr if li + CW + 1 <= SW else a[:, li:li + CW].astype(np.float32)
        enc.stdin.write(cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA).clip(0, 255).astype(np.uint8).tobytes()); n += 1
    info[c] = {"offset": off, "frames": n, "head_x_out": None}
    off += n / 30; print(c, n, "frames", "x range", int(xs.min()), int(xs.max()), flush=True)
enc.stdin.close(); enc.wait()
# audio: first stream of each clip, same length as its video
parts = []
for c in CLIPS:
    d = info[c]["frames"] / 30
    parts.append(f"[{len(parts)}:a:0]aresample=48000,apad=whole_dur={d},atrim=end={d}[a{len(parts)}]")
cmd = ["ffmpeg", "-y", "-loglevel", "error"] + sum([["-i", SRC + c + ".MOV"] for c in CLIPS], []) + [
    "-filter_complex", ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=0:a=1[a]",
    "-map", "[a]", "-ac", "1", "-c:a", "pcm_s16le", J + "/t/master_a.wav"]
subprocess.run(cmd, check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/t/master_v.mkv", "-i", J + "/t/master_a.wav", "-c", "copy", J + "/master.mkv"], check=True)
json.dump(info, open(J + "/master.json", "w"), indent=1)
