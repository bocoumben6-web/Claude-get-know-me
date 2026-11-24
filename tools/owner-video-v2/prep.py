"""cut_a.wav (audio by plan), subs.ass, m_bursts.json"""
import sys, json, subprocess, numpy as np
from scipy.signal import butter, sosfiltfilt
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job7"
sys.path.insert(0, J)
from plan import P, SUBS, out_time, TOTAL, LOGO, TONE
g = []
for i, (s, e, n) in enumerate(P):
    s, e = round(s * 30) / 30, round(e * 30) / 30
    g.append(f"[0:a]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={e-s-0.02:.4f}:d=0.02[a{i}];")
n = len(P)
g.append(f"[0:a]atrim=start={TONE[0]}:end={TONE[1]},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,apad=whole_dur={LOGO},atrim=end={LOGO},afade=t=out:st={LOGO-0.25}:d=0.25[a{n}];")
g.append("".join(f"[a{i}]" for i in range(n + 1)) + f"concat=n={n+1}:v=0:a=1[a]")
open(J + "/agraph.txt", "w").write("\n".join(g))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/master.mkv", "-filter_complex_script", J + "/agraph.txt", "-map", "[a]", "-ar", "48000", "-ac", "1", J + "/cut_a.wav"], check=True)
def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Bebas Neue,72,&H0038CCF0,&H0038CCF0,&H00000000,&H50000000,0,0,0,0,100,100,0.5,0,1,0,3,8,110,110,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
for k, (s, e, t) in enumerate(SUBS):
    if not SUBS: break
    txt = t
    while "*" in txt: txt = txt.replace("*", "{\\c&HE4F0FC&}", 1).replace("*", "{\\r}", 1)
    ev.append(f"Dialogue: 0,{ts(out_time(s) - 0.03)},{ts(min(out_time(e) + 0.06, out_time(SUBS[k+1][0]) - 0.04) if k + 1 < len(SUBS) else min(out_time(e) + 0.06, TOTAL - 0.02))},Sub,,0,0,0,,{{\\an8\\pos(540,1100)}}{txt}")
open(J + "/subs.ass", "w").write(head + "\n".join(ev) + "\n")
# speech bursts on the master (for the cut check)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/master.mkv", "-f", "f32le", "-ac", "1", "-ar", "16000", J + "/t/m.raw"])
a = np.fromfile(J + "/t/m.raw", dtype=np.float32); b = sosfiltfilt(butter(4, [250, 3200], btype="band", fs=16000, output="sos"), a)
e = np.sqrt(np.convolve(b ** 2, np.ones(400) / 400, "same")[::160]); db = 20 * np.log10(e + 1e-9)
bursts = []
for c0, c1 in ((0, len(db) / 100),):
    seg = db[int(c0 * 100):int(c1 * 100)]; thr = np.percentile(seg[seg > -150], 10) + 12; on = seg > thr; i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]: j += 1
            if j - i >= 5: bursts.append((round(c0 + i / 100, 2), round(c0 + j / 100, 2)))
            i = j
        else: i += 1
json.dump(bursts, open(J + "/m_bursts.json", "w"))
print("TOTAL %.2f s + logo %.1f; subs %d; bursts %d" % (TOTAL, LOGO, len(ev), len(bursts)))
