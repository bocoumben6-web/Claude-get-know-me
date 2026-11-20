"""Final audio: speech (cleaned) -> phrase level rides -> gain to target -> + sounds -> transparent peak limiter.
The limiter only touches real peaks, so sounds never push the voice down."""
import sys, json, wave, subprocess, numpy as np
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job5"
SR = 48000; CEIL = 0.84
def rd(p):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/" + p, "-f", "f32le", "-ac", "2", "-ar", str(SR), J + "/t/r.raw"])
    return np.fromfile(J + "/t/r.raw", dtype=np.float32).reshape(-1, 2).astype(np.float64)
def wr(p, x):
    with wave.open(J + "/" + p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        v = (np.clip(x, -1, 1) * 8388607).astype("<i4"); w.writeframes(v.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
def limiter(x, ceil=CEIL, look=0.004, rel=0.050):
    pk = np.abs(x).max(1); need = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    L = int(look * SR)
    g = np.minimum.reduce([np.roll(need, -k) for k in range(0, L + 1, 8)] + [np.roll(need, k) for k in range(1, 9)])   # hold over the look-ahead
    a = np.exp(-1 / (rel * SR)); out = np.empty_like(g); z = 1.0
    for i in range(len(g)):
        z = g[i] if g[i] < z else a * z + (1 - a) * g[i]; out[i] = z
    k = np.ones(L) / L; out = np.minimum(np.convolve(out, k, mode="same"), g)
    return x * out[:, None], float((out < 0.999).mean())
def lufs(p):
    e = subprocess.run(["ffmpeg", "-i", J + "/" + p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    import re; return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", e)[-1])

sys.path.insert(0, J)
from plan import SUBS, out_time
sp = rd("a_voice.wav"); n = len(sp)
# phrase rides: even out phrases that are clearly louder or quieter than the rest (max +3.5 / -3 dB, smooth 80 ms ramps)
_db = lambda v: 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9); _m = sp.mean(1); lv = []
for s_, e_, _t in SUBS:
    a_, b_ = int(out_time(s_) * SR), int(out_time(e_) * SR); w_ = sorted(_db(_m[i:i + 2400]) for i in range(a_, b_ - 2400, 1200))
    lv.append((out_time(s_), out_time(e_), float(np.mean(w_[int(len(w_) * 0.4):]))))
med = float(np.median([l for _, _, l in lv])); rides = []
g = np.ones(n)
for a, b, l in lv:
    d = float(np.clip(med - l, -2.0, 2.0)) if abs(med - l) > 1.2 else 0.0; rides.append([round(a, 2), round(b, 2), round(d, 2)])
    if d: g[int(max(0, a - 0.06) * SR):int((b + 0.06) * SR)] = 10 ** (d / 20)
json.dump(rides, open(J + "/rides.json", "w"))
k = np.hanning(int(0.08 * SR)); k /= k.sum(); g = np.convolve(g, k, mode="same")
sp = sp * g[:, None]
k0 = 0.9 / max(1e-6, np.abs(sp).max())         # provisional gain just to measure (never clips, works for quiet and loud sources)
wr("t/ride.wav", sp * k0)
gain = k0 * 10 ** ((-14.0 - lufs("t/ride.wav") + 0.5) / 20)
sp, act0 = limiter(sp * gain)
wr("a_speech.wav", sp)
sx = rd("sfx.wav")[:n] if "--nosfx" not in sys.argv else np.zeros_like(sp)
mix, act = limiter(sp + sx)
wr("a_mix.wav", mix)
print("Sprache: Begrenzer aktiv in %.2f %% der Zeit | Mischung: %.2f %% | Lautheit Mischung %.1f LUFS | Spitze %.3f" % (act0 * 100, act * 100, lufs("a_mix.wav"), np.abs(mix).max()))
