"""Owner-Vlog bauen: Segmente -> GTA-Switches -> Ton -> Untertitel -> Export.
Aufruf: JOB=<ordner> python3 build.py   (plan.py liegt daneben)"""
import os, sys, json, subprocess, wave, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import *
import noisereduce as nr
from scipy.signal import butter, sosfiltfilt

W, H, FPS, SR = 1920, 1080, 30, 48000
FONTDIR = os.path.abspath(os.path.dirname(__file__) + "/../../assets/fonts")
T = JOB + "/build"; os.makedirs(T, exist_ok=True)
run = lambda *a: subprocess.run(list(a), check=True)
FF = ["ffmpeg", "-y", "-loglevel", "error"]
ENC = ["-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", str(FPS)]

def clip(c): return f"{CLIPS}/IMG_{c}.MOV"

# ---------- 1. Bild-Segmente ----------
def vf_for(c):
    if c in PORTRAIT:
        return (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=45,eq=brightness=-0.08[bg];"
                f"[b]scale=-2:{H}[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1,fps={FPS}")
    rot = ROTATE.get(c, "")
    return f"[0:v]{rot + ',' if rot else ''}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"

items = []   # (kind, path, dur, seg)
for i, s in enumerate(SEGMENTS):
    if s == "SWITCH":
        items.append(["switch", f"{T}/sw{i:02d}.mp4", SWITCH_LEN, None]); continue
    c, a, b, mode = s
    p = f"{T}/seg{i:02d}.mp4"
    n = round((b - a) * FPS)
    if not os.path.exists(p): run(*FF, "-ss", f"{a:.3f}", "-i", clip(c), "-filter_complex", vf_for(c), "-frames:v", str(n), "-an", *ENC, p)
    items.append(["seg", p, n / FPS, s])

# ---------- 2. GTA-Switch ----------
def grab(p, last):
    args = ["-sseof", "-0.1"] if last else []
    out = subprocess.run(["ffmpeg", "-loglevel", "error", *args, "-i", p, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.uint8)[-W * H * 3:].reshape(H, W, 3).astype(np.float32)

def look(img, k):
    """k 0..1: wie hoch die Kamera ist -> entsättigt, kühl, flacher Kontrast, etwas heller (Luft)"""
    g = img.mean(2, keepdims=True)
    x = img * (1 - 0.85 * k) + g * 0.85 * k
    x = x * np.array([1 + 0.10 * k, 1 + 0.03 * k, 1 - 0.04 * k], np.float32)   # BGR: leicht kühl
    x = (x - 128) * (1 - 0.30 * k) + 128 + 14 * k
    return x

def make_sky(seed):
    """blasser, entsättigter Himmel mit weichen Wolken (selbst erzeugt)"""
    r = np.random.default_rng(seed); SH = int(H * 1.3); SW = W * 2
    n = np.zeros((SH, SW), np.float32)
    for sc, amp in [(8, 1.0), (16, .5), (32, .25), (64, .12)]:
        n += cv2.resize(r.random((max(2, SH * sc // SW + 1), sc)).astype(np.float32), (SW, SH), interpolation=cv2.INTER_CUBIC) * amp
    n = (n - n.min()) / (n.max() - n.min()); cl = np.clip((n - 0.45) * 2.2, 0, 1)[..., None]
    y = np.linspace(0, 1, SH, dtype=np.float32)[:, None, None]
    top, hor = np.array([150, 118, 96], np.float32), np.array([222, 214, 206], np.float32)   # BGR
    sky = top * (1 - y) + hor * y
    return sky * (1 - cl * 0.7) + 238 * cl * 0.7

def canvas(img, sky):
    """Himmel über dem Bild, weicher Übergang"""
    SH = sky.shape[0]; out = np.concatenate([sky[:, :W], img], 0)
    m = np.zeros((SH + H, 1, 1), np.float32); m[SH:] = 1
    ramp = int(H * 0.35)
    m[SH:SH + ramp] = np.linspace(0, 1, ramp, dtype=np.float32)[:, None, None]
    sky_ext = np.concatenate([sky[:, :W], np.repeat(sky[-1:, :W], H, 0)], 0)
    return out * m + sky_ext * (1 - m), SH

def view(cv, y0, blur):
    y0 = int(np.clip(y0, 0, cv.shape[0] - H)); v = cv[y0:y0 + H]
    k = int(blur)
    return cv2.blur(v, (1, k)) if k > 2 else v

def whip_frames(A, B, n=12):
    """Whip-Pan: A reißt nach links weg, B zieht von rechts rein. Unschärfe folgt dem Tempo."""
    cv = np.concatenate([A, B], 1); fr = []
    pos = lambda t: t * t * (3 - 2 * t)                       # langsam -> schnell -> langsam
    pos2 = lambda t: pos(pos(t))                              # noch schärferer Riss in der Mitte
    for f in range(n):
        t0, t1 = f / n, (f + 1) / n
        x = W * pos2((t0 + t1) / 2); speed = W * (pos2(t1) - pos2(t0))
        v = cv[:, int(x):int(x) + W]
        k = int(speed * 1.1)
        fr.append(cv2.blur(v, (k, 1)) if k > 2 else v)
    return fr

for i, it in enumerate(items):
    if it[0] != "switch": continue
    A, B = grab(items[i - 1][1], True), grab(items[i + 1][1], False)
    fr = whip_frames(A, B)
    it[2] = len(fr) / FPS
    p = subprocess.Popen([*FF, "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *ENC, it[1]], stdin=subprocess.PIPE)
    for f in fr: p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

# Zeitachse
t = 0.0; timeline = []
for it in items:
    timeline.append((t, it)); t += it[2]
TOTAL = t
with open(f"{T}/list.txt", "w") as f:
    for _, it in timeline: f.write(f"file '{it[1]}'\n")
run(*FF, "-f", "concat", "-safe", "0", "-i", f"{T}/list.txt", "-c", "copy", f"{T}/video.mp4")

# ---------- 3. Ton ----------
def load(c):
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", clip(c), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(out, np.float32).astype(np.float64)
hp = lambda x, f: sosfiltfilt(butter(2, f, "hp", fs=SR, output="sos"), x)
clean = {}
for c in {s[0] for s in SEGMENTS if s != "SWITCH" and s[3] == "voice"}:
    x = hp(load(c), 75); a, b = NOISE[c]
    clean[c] = nr.reduce_noise(y=x, sr=SR, y_noise=x[int(a * SR):int(b * SR)], stationary=True, prop_decrease=0.70, n_fft=2048)[:len(x)]

voice = np.zeros(int((TOTAL + 0.5) * SR)); musicmask = np.zeros_like(voice)
fade = int(0.012 * SR)
for t0, it in timeline:
    i0 = int(t0 * SR); n = int(it[2] * SR)
    if it[0] == "seg" and it[3][3] == "voice":
        c, a, b, _ = it[3]; x = clean[c][int(a * SR):int(a * SR) + n].copy()
        r = np.sqrt(np.mean(x[np.abs(x) > np.percentile(np.abs(x), 60)] ** 2)) + 1e-9
        x *= min(10 ** (-20 / 20) / r, 6.0)                   # Sätze ungefähr gleich laut
        w = np.ones(len(x)); w[:fade] = np.linspace(0, 1, fade); w[-fade:] = np.linspace(1, 0, fade)
        voice[i0:i0 + len(x)] += x * w
    else:
        musicmask[i0:i0 + n] = 1

# Switch-Sound: drei dumpfe Schläge raus, Luftzug beim Schwenk, drei rein (selbst erzeugt)
rng = np.random.default_rng(7)
def thump(f0=110, f1=48, d=0.22):
    tt = np.arange(int(d * SR)) / SR; f = f1 + (f0 - f1) * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 16)
def air(d=0.35):
    nz = rng.standard_normal(int(d * SR)); tt = np.linspace(0, 1, len(nz))
    out = np.zeros_like(nz); fc = 400 + 3000 * np.sin(np.pi * tt)
    y = 0.0
    for k in range(len(nz)):
        a = np.exp(-2 * np.pi * fc[k] / SR); y = (1 - a) * nz[k] + a * y; out[k] = y
    return out * np.sin(np.pi * tt) ** 1.5 * 2.2
sfx = np.zeros_like(voice)
def put(tt, s, g):
    i = int(tt * SR); sfx[i:i + len(s)] += s[:len(sfx) - i] * g
for t0, it in timeline:
    if it[0] != "switch": continue
    put(t0 + it[2] / 2 - 0.16, air(0.32), 0.40)             # ein Whoosh, Mitte des Risses

mix = voice + sfx
def w24(p, x):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        v = (np.clip(np.stack([x, x], 1), -1, 1) * 8388607).astype("<i4"); w.writeframes(v.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
w24(f"{T}/mix_raw.wav", mix[:int(TOTAL * SR)])
run(*FF, "-i", f"{T}/mix_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", f"{T}/mix.wav")

# ---------- 4. Untertitel (Wort für Wort aufbauend) ----------
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
def src_to_out(c, x):
    for t0, it in timeline:
        if it[0] == "seg" and it[3][0] == c and it[3][1] - 0.02 <= x <= it[3][2] + 0.02:
            return t0 + min(max(x - it[3][1], 0), it[2])
    return None
ev = []
for c, words, end in SUBS:
    for k, (wd, st) in enumerate(words):
        a = src_to_out(c, st); b = src_to_out(c, words[k + 1][1]) if k + 1 < len(words) else src_to_out(c, end)
        if a is None or b is None or b - a < 0.03: continue
        ev.append((a, b, " ".join(x[0] for x in words[:k + 1])))
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Bebas Neue,84,&H0038CCF0,&H0038CCF0,&H80000000,&H64000000,0,0,0,0,100,100,1,0,1,1.2,2.5,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for a, b, txt in ev:
    ass += f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\pos({W // 2},{int(H * 0.52)})}}{txt}\n"
open(f"{T}/subs.ass", "w").write(ass)

# ---------- 5. Export ----------
OUT = JOB + "/export"; os.makedirs(OUT, exist_ok=True)
run(*FF, "-i", f"{T}/video.mp4", "-i", f"{T}/mix.wav", "-vf", f"subtitles={T}/subs.ass:fontsdir={FONTDIR}",
    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-maxrate", "25M", "-bufsize", "50M", "-preset", "slow",
    "-profile:v", "high", "-level", "4.2", "-r", "30", "-g", "60", "-pix_fmt", "yuv420p",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
    "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", f"{OUT}/vlog_v1.mp4")

# Musik-Stellen (stumm) als Liste
spans = []; inside = False
for t0, it in timeline:
    m = it[0] == "switch" or it[3][3] == "music"
    if m and not inside: spans.append([t0, t0 + it[2]]); inside = True
    elif m: spans[-1][1] = t0 + it[2]
    else: inside = False
json.dump({"total": TOTAL, "music": spans, "subs": ev,
           "timeline": [(t0, it[0], it[2], it[3]) for t0, it in timeline]}, open(f"{T}/timeline.json", "w"), indent=1)
print("Länge %.2f s" % TOTAL)
for a, b in spans: print("Musik %5.2f – %5.2f" % (a, b))
