"""Checks every cut of a plan for clipped word edges, including soft high-frequency sounds (s, z, ch, f, t).
For each cut: energy in 250-3200 Hz (voice) and 2500-7500 Hz (fricatives), 20 ms steps.
A cut edge is bad if speech energy (either band, > floor + 10 dB) continues within 60 ms on the removed side."""
import sys, subprocess, numpy as np
from scipy.signal import butter, sosfiltfilt
J = sys.argv[1]; sys.path.insert(0, J)
from plan import P
SR = 32000
a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", J + "/master.mkv", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout, np.float32)
def env(lo, hi):
    b = sosfiltfilt(butter(4, [lo, hi], btype="band", fs=SR, output="sos"), a)
    h = int(0.02 * SR); n = len(b) // h
    return 20 * np.log10(np.sqrt((b[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
E1, E2 = env(250, 3200), env(2500, 7500)
f1 = np.percentile(E1[E1 > -150], 10); f2 = np.percentile(E2[E2 > -150], 10)
sp = (E1 > f1 + 10) | (E2 > f2 + 10)
def run_from(i, step):   # how long speech continues from frame i in direction step
    k = 0
    while 0 <= i + step * k < len(sp) and sp[i + step * k]: k += 1
    return k * 0.02
bad = []
for s, e, n in P:
    i_s = int(round(s / 0.02)); i_e = int(round(e / 0.02))
    before_start = run_from(i_s - 1, -1)    # speech right before the piece start (removed side)
    after_end = run_from(i_e, +1)           # speech right after the piece end (removed side)
    in_start = sp[i_s:i_s + 3].any(); in_end = sp[max(0, i_e - 3):i_e].any()
    if in_start and before_start > 0.0: bad.append((n, "Anfang", s, round(before_start, 2)))
    if in_end and after_end > 0.0: bad.append((n, "Ende", e, round(after_end, 2)))
    # suggestion: where speech really stops after the end
    print(f"{n:8s} {s:7.2f}-{e:7.2f}  Anfang: Sprache davor {before_start:.2f}s (drin {in_start})  Ende: Sprache danach {after_end:.2f}s (drin {in_end})")
print("VERDÄCHTIG:" if bad else "OK: kein Schnitt in einem Laut", bad)
import json; open(J + "/cutcheck.json", "w").write(json.dumps([[n, w] for n, w, _, _ in bad]))
