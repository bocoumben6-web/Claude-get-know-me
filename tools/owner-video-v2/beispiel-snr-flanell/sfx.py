"""Sound design for the Lavish owner video. All sounds are synthesized here (no samples).
Writes sfx.wav (stereo, 48 kHz, same length as the video) and sfx_cues.json."""
import sys, json, wave, numpy as np
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job3"
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
# hook: title pops in, impact when it has landed
add(0.0, riser(0.45), 0.034, "riser")
add(0.62, impact(0.9), 0.036, "impact")
# "Still Not Reachable": bar drops in (whoosh sits in the pause before the sentence)
add(st("snr") - 0.10, whoosh(0.20, 700, 4200), 0.10, "whoosh")
# punch-in "Ich erzähle euch die Besonderheiten"
add(st("beso") - 0.03, whoosh(0.18, 300, 2200), 0.05, "whoosh")
# hem
add(st("saum") - 0.11, whoosh(0.20), 0.10, "whoosh")
add(st("dist") - 0.03, click(), 0.10, "click")
# patches: bar in the cut; nothing on the spoken "drei"
add(st("patch") - 0.11, whoosh(0.20, 700, 3600), 0.10, "whoosh")
add(st("nacken") - 0.02, pop(460, 160, 0.08), 0.06, "pop")
add(st("ruecken") - 0.02, pop(520, 170, 0.08), 0.06, "pop")
add(st("seite") - 0.02, pop(600, 190, 0.08), 0.06, "pop")
# the flannel, five patterns (soft ticks for the five swatches), fashion / art
# no whoosh before "Ich meine ...": the cut is too tight, it covered the end of "unten links" (measured)
tick_roll(o(25.14), 0.68, 5, 0.020, 1900, 2700)
add(o(26.92) + 0.04, pop(360, 120, 0.12), 0.08, "pop")
add(st("art") - 0.03, click(), 0.09, "click")
# fit
add(st("fit") - 0.11, whoosh(0.20, 500, 3400), 0.10, "whoosh")
# closing lines: push-in
add(st("rockt") - 0.11, whoosh(0.20, 300, 2000), 0.07, "whoosh")
# logo card
add(TOTAL + 0.02, impact(1.25, 84, 38), 0.13, "impact-logo")

pk = np.abs(bus).max()
print("sfx peak %.3f, cues %d" % (pk, len(cues)))
with wave.open(J + "/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(bus, -1, 1) * 32767).astype("<i2").tobytes())
json.dump(sorted(cues), open(J + "/sfx_cues.json", "w"))
