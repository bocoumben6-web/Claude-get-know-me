"""Suggest safe piece ends: if speech (voice band OR 2.5-7.5 kHz fricative band) continues after a cut,
extend the end to the first real gap (or the deepest dip within 0.40 s) + 40 ms."""
import sys, subprocess, re, numpy as np
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
lvl = np.maximum(E1 - f1, E2 - f2)      # dB above floor, whichever band is louder
out = []
for s, e, n in P:
    i = int(round(e / 0.02)); k = 0
    while i + k < len(lvl) and lvl[i + k] > 10: k += 1
    new = e
    if k > 0:
        if k * 0.02 <= 0.40: new = e + k * 0.02 + 0.04
        else:
            w = lvl[i:i + 20]; j = int(np.argmin(w)); new = e + j * 0.02 + 0.02
    nxt = [ps for ps, pe, pn in P if ps > s]
    out.append((s, round(new, 2), n, round(new - e, 2)))
for s, ne, n, d in out: print(f"{n:8s} end {ne:.2f} (+{d:.2f})")
if "--write" in sys.argv:
    src = open(J + "/plan.py").read()
    for (s, e, n), (_, ne, _, d) in zip(P, out):
        if d > 0:
            src, c = re.subn(r'\((\s*[0-9.]+),\s*[0-9.]+,\s*"' + n + r'"\)', lambda m: f'({m.group(1)}, {ne:.2f}, "{n}")', src, count=1)
            assert c == 1, n
    open(J + "/plan.py", "w").write(src); print("plan.py updated")
