"""Speech segments from both bands (voice 250-3200 Hz + fricatives 2.5-7.5 kHz), 20 ms grid, gaps >= 80 ms split segments."""
import sys, subprocess, numpy as np
from scipy.signal import butter, sosfiltfilt
J = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
SR = 32000; GAP = int(sys.argv[4]) if len(sys.argv) > 4 else 4
a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", J + "/master.mkv", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout, np.float32)
def env(lo, hi):
    b = sosfiltfilt(butter(4, [lo, hi], btype="band", fs=SR, output="sos"), a)
    h = int(0.02 * SR); n = len(b) // h
    return 20 * np.log10(np.sqrt((b[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
E1, E2 = env(250, 3200), env(2500, 7500)
f1 = np.percentile(E1[E1 > -150], 10); f2 = np.percentile(E2[E2 > -150], 10)
sp = (E1 > f1 + 10) | (E2 > f2 + 10)
segs = []; i = 0
while i < len(sp):
    if sp[i]:
        j = i
        while j < len(sp) and sp[j]: j += 1
        if segs and i - segs[-1][1] < GAP: segs[-1][1] = j
        else: segs.append([i, j])
        i = j
    else: i += 1
print(" ".join(f"{s*0.02:.2f}-{e*0.02:.2f}" for s, e in segs if e - s >= 3 and t0 <= s * 0.02 <= t1))
