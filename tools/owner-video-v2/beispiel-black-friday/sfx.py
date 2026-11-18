"""Sound design for the Lavish owner video. All sounds are synthesized here (no samples).
Writes sfx.wav (stereo, 48 kHz, same length as the video) and sfx_cues.json."""
import sys, json, wave, numpy as np
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job4"
sys.path.insert(0, J)
from plan import out_time as o, piece_out, TOTAL, LOGO
SR = 48000
rng = np.random.default_rng(5)
N = int(round((TOTAL + LOGO) * SR))
bus = np.zeros((N, 2), np.float32)
cues = []

def env_ad(n, a=0.004, tau=0.08):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / tau)

def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * np.asarray(fc, dtype=np.float64) / SR) * np.ones(len(x))
    y = np.zeros(len(x)); z = 0.0
    for i in range(len(x)):
        z = (1 - a[i]) * x[i] + a[i] * z; y[i] = z
    return y

def bandpass_sweep(x, f_lo, f_hi):
    """band between two sweeping one-pole filters"""
    return onepole_lp(x, f_hi) - onepole_lp(x, f_lo)

def whoosh(d=0.34, f0=500, f1=3800, peak=0.62, bright=1.0):
    n = int(d * SR); t = np.arange(n) / n
    noise = rng.normal(0, 1, n)
    fc = f0 + (f1 - f0) * np.sin(np.pi * np.clip(t / peak / 2, 0, 0.5)) ** 2 * (t <= peak) + (f1 - (f1 - f0) * 0.6 * (t - peak) / (1 - peak)) * (t > peak)
    y = bandpass_sweep(noise, fc * 0.45, fc * 1.6 * bright)
    e = np.where(t < peak, (t / peak) ** 2.2, ((1 - t) / (1 - peak)) ** 1.6)
    y = y * e; y /= np.abs(y).max() + 1e-9
    pan = 0.35 + 0.30 * t                       # drifts slightly left -> right
    return np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1) * 1.3

def pop(f0=430, f1=150, d=0.10):
    n = int(d * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.030)
    y[:int(0.002 * SR)] += rng.normal(0, 0.25, int(0.002 * SR))
    return np.stack([y, y], 1)

def tick(f=2300):
    n = int(0.030 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) + rng.normal(0, 0.35, n) * np.exp(-t / 0.0015)
    return np.stack([y, y], 1)

def click():
    n = int(0.05 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 1500 * t) * np.exp(-t / 0.010) + 0.6 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.005)
    return np.stack([y, y], 1)

def bell(f0=1318.5, d=0.9, tau=0.24):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, (m, a, dk) in enumerate([(1.0, 1.0, 1.0), (2.0, 0.42, 0.7), (2.76, 0.30, 0.5), (5.4, 0.16, 0.3)]):
        y += a * np.sin(2 * np.pi * f0 * m * t + k) * np.exp(-t / (tau * dk))
    y *= np.minimum(1, t / 0.002)
    return np.stack([y, y * 0.96], 1) / 1.6

def chime(tail=1.0):
    """original two-note rising chime (not any app's notification sound)"""
    a = bell(1174.7, 0.7 * tail, 0.20 * tail); b = bell(1568.0, 0.85 * tail, 0.24 * tail)
    out = np.zeros((int(0.095 * SR) + len(b), 2)); out[:len(a)] += a; out[int(0.095 * SR):] += b
    return out

def impact(d=1.1, f0=92, f1=44):
    n = int(d * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.26) * np.minimum(1, t / 0.003)
    th = onepole_lp(rng.normal(0, 1, n), 420) * np.exp(-t / 0.045) * 2.2
    y = np.tanh((y + th) * 1.4) / 1.2
    return np.stack([y, y], 1)

def riser(d=0.52):
    n = int(d * SR); t = np.arange(n) / n
    y = bandpass_sweep(rng.normal(0, 1, n), 300 + 1500 * t ** 2, 1500 + 7000 * t ** 2) * t ** 2.4
    y /= np.abs(y).max() + 1e-9
    return np.stack([y, y], 1)

def add(t, snd, gain, name):
    i = int(round(t * SR))
    if i < 0: snd = snd[-i:]; i = 0
    j = min(N, i + len(snd)); bus[i:j] += (snd[:j - i] * gain).astype(np.float32)
    cues.append([round(t, 3), name, gain, round(len(snd) / SR, 3)])   # start, name, gain, length

def tick_roll(t0, dur, n, gain, f0=1900, f1=2900):
    for k in range(n):
        add(t0 + dur * (k / max(1, n - 1)) ** 0.8, tick(f0 + (f1 - f0) * k / max(1, n - 1)), gain, "tick")

# ---------------- cues (same times as the graphics) ----------------
st = lambda n: piece_out(n)[0]
# hook: letters pop in, soft hit when the title stands
add(0.0, riser(0.42), 0.03, "riser")
add(0.60, impact(0.8), 0.034, "impact")
add(st("q2") - 0.06, whoosh(0.16, 300, 2200), 0.05, "whoosh")          # punch-in between the two questions
# BLACK FRIDAY slams in, then gets struck through (scratch + camera hit)
add(o(3.80), pop(300, 110, 0.09), 0.06, "pop")
add(o(4.50) + 0.02, whoosh(0.14, 2500, 6500, peak=0.3), 0.06, "strike")
add(o(4.50) + 0.06, impact(0.5, 120, 60), 0.05, "hit")
# "Aktion?" bar
add(st("aktion") - 0.11, whoosh(0.20, 600, 3200), 0.08, "whoosh")
add(o(7.70), pop(480, 160, 0.08), 0.05, "pop")
# "Beanies": hit, then the photo carousel clicks through
add(st("beanies") - 0.11, whoosh(0.20, 700, 3600), 0.08, "whoosh")
add(o(13.08) + 0.02, pop(340, 120, 0.08), 0.05, "pop")
_, e_be = piece_out("beanies"); t_bn = o(13.08); seg = (e_be - (t_bn + 0.14)) / 4
for i in range(3): add(t_bn + 0.14 + i * seg, click(), 0.025, "click")   # the 4th photo comes in silently (it lands on "aber sonst")
# "Ah!": the news. Hit in the cut, three secret colorways flip in with ticks
# no whoosh before "Ah": "aber sonst..." runs right up to the cut (measured); the hit on "Ah" carries it
add(st("ah") + 0.02, impact(0.7, 100, 50), 0.028, "impact")
for i in range(3): add(st("ah") + 0.34 + i * 0.16, tick(2100 + 300 * i), 0.03, "tick")
# "ihr müsst mir helfen": info bar
add(st("helfen") + 0.20, pop(560, 180, 0.07), 0.045, "pop")
# logo card
add(TOTAL + 0.02, impact(1.25, 84, 38), 0.13, "impact-logo")

pk = np.abs(bus).max()
print("sfx peak %.3f, cues %d" % (pk, len(cues)))
with wave.open(J + "/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(bus, -1, 1) * 32767).astype("<i2").tobytes())
json.dump(sorted(cues), open(J + "/sfx_cues.json", "w"))
