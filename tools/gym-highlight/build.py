#!/usr/bin/env python3
"""Gym-Highlight (Owner, 28.11.2026): VHS + iPhone-Clean gemischt, Fokus Gym + Lavish-Beanie.
Musik (Meek Mill – Millidelphia) legt der Owner in TikTok drunter; hier nur Umgebungston.

Aufruf: build.py RAW_DIR WORK_DIR OUT.mp4
RAW_DIR = entpackter Dropbox-Ordner mit den .mov-Dateien.
"""
import subprocess, sys, os

RAW, WORK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO = os.path.join(ROOT, "assets", "logo.png")
os.makedirs(WORK, exist_ok=True)

SRC = {  # id -> (Datei, Typ)
    "c02": ("Video 28.11.26, 01 43 00.mov", "vhs"),
    "c03": ("Video 28.11.26, 01 43 27.mov", "clean"),
    "c04": ("Video 28.11.26, 01 43 51.mov", "vhs"),
    "c05": ("Video 28.11.26, 01 44 06.mov", "clean"),
    "c06": ("Video 28.11.26, 01 54 15.mov", "vhs"),
    "c07": ("Video 28.11.26, 01 54 37.mov", "clean"),
    "c09": ("Video 28.11.26, 01 56 08.mov", "vhs"),
    "c10": ("Video 28.11.26, 01 56 24.mov", "vhs"),
    "c12": ("Video 28.11.26, 02 52 01.mov", "clean"),
}

# (clip, start, Quelldauer, Tempo [0.5 = Slow-Mo], Optionen)
# vhs_x: Ausschnitt im 480er VHS-Bild (0 = Datum/Uhrzeit sichtbar, 120 = ohne)
PLAN = [
    # Hook-Burst: sofort nah, Beanie im ersten Bild
    ("c05", 9.55, 0.30, 0.5, {}),
    ("c02", 0.85, 0.27, 1.0, {"vhs_x": 110}),
    ("c09", 6.30, 0.27, 1.0, {}),
    ("c06", 0.45, 0.27, 1.0, {}),
    ("c12", 4.55, 0.14, 0.5, {}),
    ("c03", 6.10, 0.27, 1.0, {}),
    # Beanie aufsetzen (VHS)
    ("c02", 0.60, 2.00, 1.0, {"vhs_x": 110}),
    # Gym: Scheibe laden (Slow-Mo), Deadlift, Gürtel
    ("c03", 1.20, 1.20, 0.5, {}),
    ("c04", 0.50, 1.80, 1.0, {}),
    ("c05", 3.40, 1.00, 0.5, {}),
    # Klimmzüge von unten, Kabelzug im Ringlicht (Underground)
    ("c07", 2.00, 1.30, 1.0, {}),
    ("c10", 1.50, 1.70, 1.0, {}),
    ("c07", 15.40, 1.20, 1.0, {}),
    # Beanie-Momente zum Schluss
    ("c09", 5.20, 2.00, 1.0, {"freeze": 0.45}),
    ("c12", 3.60, 1.60, 0.5, {}),
    ("c05", 9.50, 0.80, 0.5, {"logo_tail": 0.0}),
]

HDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
       "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
# Clean: dunkler, Lichter gedrückt, entsättigt, kühl (wie Referenz)
G_CLEAN = ("eq=contrast=1.10:saturation=0.70:gamma=0.90,"
           "curves=all='0/0.02 0.25/0.17 0.6/0.52 1/0.86',"
           "colorbalance=rs=-0.05:gs=0.0:bs=0.05:rm=-0.04:bm=0.04:rh=-0.03:bh=0.02,"
           "vignette=PI/4.5")
# VHS: Grünstich etwas Richtung Petrol, Schwarz tiefer
G_VHS = ("eq=contrast=1.08:saturation=0.85:gamma=0.95,"
         "colorbalance=gs=-0.04:bs=0.03:gm=-0.04:bm=0.02,"
         "curves=all='0/0 0.2/0.15 1/0.95',vignette=PI/5")

FPS = 30
parts = []
for i, (cid, ss, dur, speed, opt) in enumerate(PLAN):
    f, kind = SRC[cid]
    src = os.path.join(RAW, f)
    out = os.path.join(WORK, f"seg{i:02d}.mp4")
    if kind == "clean":
        vf = HDR + "scale=1080:1920:flags=lanczos," + G_CLEAN
    else:
        x = opt.get("vhs_x", 120)
        vf = f"crop=360:640:{x}:0,scale=1080:1920:flags=lanczos," + G_VHS
    vf += f",setpts=(PTS-STARTPTS)/{speed},fps={FPS}"
    out_dur = dur / speed
    if "freeze" in opt:
        vf += f",tpad=stop_mode=clone:stop_duration={opt['freeze']}"
        out_dur += opt["freeze"]
    vf += ",format=yuv420p"
    af = "aresample=48000,asetpts=PTS-STARTPTS"
    if speed != 1.0:
        af += f",atempo={speed}"
    af += f",apad,atrim=0:{out_dur:.3f}"
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur}", "-i", src,
           "-vf", vf, "-af", af, "-t", f"{out_dur:.3f}",
           "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-c:a", "pcm_s16le", "-ac", "2",
           out.replace(".mp4", ".mov")]
    subprocess.run(cmd, check=True)
    parts.append(out.replace(".mp4", ".mov"))

# Logo-Schlussbild: schwarz, L in Beige-Weiß, 0,7 s
logo_seg = os.path.join(WORK, "logo.mov")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y",
                "-f", "lavfi", "-i", f"color=black:s=1080x1920:r={FPS}:d=0.7",
                "-i", LOGO, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", "[1]scale=360:-1[l];[0][l]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]",
                "-map", "[v]", "-map", "2", "-t", "0.7",
                "-c:v", "libx264", "-crf", "14", "-c:a", "pcm_s16le", logo_seg], check=True)
parts.append(logo_seg)

lst = os.path.join(WORK, "list.txt")
with open(lst, "w") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
cat = os.path.join(WORK, "cat.mov")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-c", "copy", cat], check=True)

# Endexport: Umgebungston leise (Musik kommt in TikTok drüber), tiefer Schlag aufs Logo
total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", cat]).decode())
t_logo = total - 0.7
boom = (f"aevalsrc='0.9*sin(2*PI*(55-25*t)*t)*exp(-6*t)':s=48000:d=0.7,"
        f"adelay={int(t_logo*1000)}|{int(t_logo*1000)},aformat=channel_layouts=stereo")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", cat,
                "-filter_complex",
                f"[0:a]highpass=f=60,loudnorm=I=-22:TP=-3:LRA=11[amb];{boom},volume=0.35[b];"
                f"[amb][b]amix=inputs=2:normalize=0,alimiter=limit=0.9[a]",
                "-map", "0:v", "-map", "[a]",
                "-c:v", "libx264", "-preset", "slow", "-b:v", "18M", "-maxrate", "22M", "-bufsize", "36M",
                "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", OUT], check=True)
print("fertig:", OUT, f"{total:.2f}s")
