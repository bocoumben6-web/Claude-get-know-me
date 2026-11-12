"""Pflicht-Selbstkontrolle für ein fertiges Lavish-Video. Prüft die EXPORTIERTE Datei, nicht Zwischenstände."""
import sys, json, re, subprocess, difflib, numpy as np, cv2
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job2"
sys.path.insert(0, J)
from plan import P, SUBS, out_time, TOTAL, LOGO
F = J + "/lavish_whatsapp_v1.mp4"; ok = True
def chk(name, cond, info=""):
    global ok; ok &= bool(cond); print(f"  [{'OK ' if cond else 'FEHLER'}] {name} {info}")
def run(*a): return subprocess.run(a, capture_output=True, text=True)
def frame(n):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", F, "-vf", f"select=eq(n\\,{n})", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)

print("1 TECHNIK")
pr = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", F).stdout)
v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]; a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
exp = round((TOTAL + LOGO) * 30)
chk("1080x1920", (v["width"], v["height"]) == (1080, 1920)); chk("30 fps", v["r_frame_rate"] == "30/1")
chk("H.264 / yuv420p", v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p"); chk("AAC 48 kHz Stereo", a["codec_name"] == "aac" and a["sample_rate"] == "48000" and a["channels"] == 2)
chk("Frames", int(v["nb_frames"]) == exp, f"{v['nb_frames']} / {exp}")
chk("Bild und Ton gleich lang", abs(float(v["duration"]) - float(a["duration"])) < 0.035, f"{v['duration']} / {a['duration']}")
size = int(pr["format"]["size"]) / 1e6; chk("Dateigröße < 100 MB", size < 100, f"{size:.1f} MB")
chk("keine Decode-Fehler", run("ffmpeg", "-v", "error", "-i", F, "-f", "null", "-").stderr.strip() == "")

print("2 TON")
e = run("ffmpeg", "-i", F, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
I = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", e)[-1]); pk = float(re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", e)[-1])
chk("Lautheit -14 LUFS ± 0,7", abs(I + 14) <= 0.7, f"{I} LUFS"); chk("True Peak < -1 dBFS", pk < -1.0, f"{pk} dBFS")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", F, "-f", "f32le", "-ac", "2", "-ar", "48000", J + "/final48.raw"])
x2 = np.fromfile(J + "/final48.raw", dtype=np.float32).reshape(-1, 2)
x = x2[:, np.abs(x2).max(0).argmax()]
d = np.abs(np.diff(x)); cuts = []; off = 0
for s, e_, n in P: off += round(e_ * 30) - round(s * 30); cuts.append(off / 30)
worst = max(d[int((c - 0.03) * 48000):int((c + 0.03) * 48000)].max() for c in cuts)
normal = np.percentile(d, 99.999)
chk("kein Knacken an Schnitten (Sprung nicht größer als in normaler Sprache)", worst <= normal * 1.3, f"an Schnitten max. {worst:.3f}, in normaler Sprache bis {normal:.3f}")
chk("kein Clipping", np.abs(x).max() < 0.999, f"max {np.abs(x).max():.3f}")
tail = x[int((TOTAL + 1.6) * 48000):]; chk("Ende klingt aus (still)", np.sqrt((tail ** 2).mean()) < 0.003)

print("3 SCHNITTE: keine Sprache in weggeschnittenen Bereichen")
bursts = json.load(open(J + "/m_bursts.json"))
kept = [(s, e_) for s, e_, _ in P]
ALLOWED = [(9.88, 10.23, "Geräusch am Clip-Anfang, keine Sprache"), (32.97, 33.10, None), (35.26, 36.39, "Gespräch nach dem Take")]
for b0, b1 in bursts:
    inside = any(s - 0.02 <= b0 and b1 <= e_ + 0.02 for s, e_ in kept)
    why = next((w for a0, a1, w in ALLOWED if abs(a0 - b0) < 0.05), None)
    if not inside: chk(f"Sprach-Abschnitt {b0:.2f}-{b1:.2f} bewusst entfernt", why is not None, f"({why})" if why else "NICHT BEGRÜNDET")
chk("alle übrigen Sprach-Abschnitte vollständig enthalten", all(any(s - 0.02 <= b0 and b1 <= e_ + 0.02 for s, e_ in kept) or any(abs(a0 - b0) < 0.05 for a0, _, w in ALLOWED if w) for b0, b1 in bursts))

print("4 UNTERTITEL gegen Ton des fertigen Videos")
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", F, "-f", "f32le", "-ac", "1", "-ar", "16000", J + "/final.raw"])
r, _ = m.transcribe(np.fromfile(J + "/final.raw", dtype=np.float32), language="de", beam_size=5, condition_on_previous_text=False)
heard = " ".join(s.text.strip() for s in r); print("   gehört:", heard)
norm = lambda s: re.sub(r"[^a-zäöüß0-9 ]", "", s.lower().replace("-", " ").replace("%", " prozent")).split()
H = norm(heard); U = norm(" ".join(t.replace("*", "") for _, _, t in SUBS)); sm = difflib.SequenceMatcher(None, H, U)
OKAY = {("early", "access"): "englisches Wort, wird ohne Kontext nicht erkannt; mit Kontext und vom Owner bestätigt", ("ein", "pop", "up"): "nur Schreibweise/Grammatik", ("dieselbe",): "nur Schreibweise"}
diffs = [(tuple(H[i1:i2]), tuple(U[j1:j2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
for h, u in diffs: print(f"   Abweichung: gehört {h} / Untertitel {u}  -> {OKAY.get(u, 'UNGEKLÄRT')}")
chk("jede Abweichung ist geklärt", all(u in OKAY for h, u in diffs), f"{len(diffs)} Stellen")
chk("'WhatsApp-Gruppe' am Ende vollständig hörbar", "whatsapp gruppe house of lavish" in " ".join(H))
chk("'Lavish' richtig geschrieben", "LAVISH" in " ".join(t for _, _, t in SUBS) and "LEWIS" not in " ".join(t for _, _, t in SUBS))
chk("keine Satzzeichen in Untertiteln", not re.search(r"[.,!?]", " ".join(t for _, _, t in SUBS)))

print("5 BILD")
val = open(J + "/qr_value.txt").read(); det = cv2.QRCodeDetector()
tq = [out_time(32.6), out_time(33.3), out_time(34.0), TOTAL - 0.1, TOTAL + 0.1, TOTAL + 0.6, TOTAL + 1.1, TOTAL + 1.6, TOTAL + LOGO - 0.1]
res = [det.detectAndDecode(cv2.resize(frame(int(t * 30)), (540, 960), interpolation=cv2.INTER_AREA))[0] == val for t in tq]
chk("QR-Code lesbar (auch verkleinert) im Video und im Schlussbild", all(res), str(res))
qr_dur = (TOTAL - out_time(31.96) - 0.35) + LOGO; chk("QR-Code mind. 4 s sichtbar", qr_dur >= 4.0, f"{qr_dur:.1f} s")
end = frame(int((TOTAL + LOGO / 2) * 30)); logo_area = end[310:810, 300:780]
chk("Schlussbild: Logo vorhanden", (logo_area.mean(axis=2) > 180).mean() > 0.08 and end[100:280].mean() < 25)
chk("Schlussbild: alles in der Safe-Zone (unten frei ab 1440 px)", end[1440:].mean() < 25)
chk("Schlussbild mind. 1 s", LOGO >= 1.0, f"{LOGO} s")
g = json.load(open(J + "/gfx.json"))
chk("alle Grafiken in der Safe-Zone (oben ≥ 288 px)", all(y >= 288 for _, _, _, y in g["events"]))
# face never covered: sample 3 frames per second, graphics pixels (pure yellow) inside the head box of the person mask
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
S = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad"
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=S + "/models/selfie_multiclass.tflite"), output_confidence_masks=True))
gv = cv2.VideoCapture(J + "/gfx.mkv"); bad = []; n = 0; hook_end = g["hook_end"]
import comp_boxes
while True:
    okf, fr = gv.read()
    if not okf or n >= round(TOTAL * 30): break
    if n % 10 == 0 and n / 30 > hook_end:
        t = n / 30
        r_ = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr[..., ::-1])))
        cm = r_.confidence_masks; face = (np.array(cm[3].numpy_view()).reshape(1920, 1080) > 0.5) if len(cm) > 3 else None
        if face is not None and face.any():
            ys, xs = np.where(face); box = (xs.min(), ys.min(), xs.max(), ys.max())
            for (x0, y0, x1, y1) in comp_boxes.boxes(t):
                if not (x1 < box[0] or x0 > box[2] or y1 < box[1] or y0 > box[3]): bad.append(round(t, 2))
    n += 1
chk("keine Grafik über dem Gesicht (alle 1/3 s geprüft)", not bad, str(bad[:8]))
print("\nERGEBNIS:", "ALLES BESTANDEN" if ok else "NICHT BESTANDEN")
