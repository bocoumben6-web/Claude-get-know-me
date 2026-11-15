"""Sound design for the Lavish owner video. All sounds are synthesized here (no samples).
Writes sfx.wav (stereo, 48 kHz, same length as the video) and sfx_cues.json."""
import sys, json, wave, numpy as np
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job2"
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
W_IN = 0.20          # a whoosh peaks ~0.2 s after it starts: start it early so the peak sits on the landing
# hook: count-up 0 -> 15 with ticks, impact when it lands
tick_roll(0.03, 0.50, 9, 0.030)
add(0.0, riser(0.52), 0.034, "riser")
add(0.55, impact(0.9), 0.095, "impact")
# camera push "Das erkläre ich euch jetzt"
add(piece_out("erklaer")[0] - 0.20, whoosh(0.28, 300, 2200), 0.11, "whoosh")
# website bar + page card
add(o(8.60) - W_IN + 0.10, whoosh(0.36), 0.20, "whoosh")
add(o(8.74) + 0.26, pop(380, 140), 0.20, "pop")
# yellow bar drops in from the top
add(o(10.86) - W_IN + 0.12, whoosh(0.30, 700, 4200), 0.17, "whoosh")
add(o(10.86) + 0.26, click(), 0.12, "click")
# WhatsApp link: banner jumps out -> chime
add(o(12.95), pop(520, 180), 0.13, "pop")
add(o(12.95) + 0.05, chime(0.42), 0.095, "chime")   # short: rings out before "Kommt in die ..."
# rolls to WhatsApp-Gruppe, page slides away
add(o(13.53), whoosh(0.18, 900, 3000, peak=0.5), 0.045, "whoosh")   # sits in the pause between "...Link" and "Kommt"
# benefits
# "15% DISCOUNT" bar: deliberately silent. The spoken "fünfzehn" is very short here; any sound nearby hides the first syllable.
add(o(16.18), pop(520, 170), 0.11, "pop")
add(o(17.82), pop(600, 190), 0.13, "pop")
add(o(18.90) - 0.10, whoosh(0.26, 1200, 500, peak=0.35), 0.065, "whoosh-out")
# pop-up timer: ticks up to 10, then bell + pop
add(o(20.16) - W_IN + 0.10, whoosh(0.32), 0.135, "whoosh")
tick_roll(o(20.56), 0.58, 10, 0.022, 1700, 2700)
t10 = o(20.56) + 0.62
add(t10 + 0.02, bell(1568.0, 1.0, 0.30), 0.036, "bell")
add(t10 + 0.05, pop(360, 120, 0.13), 0.043, "pop")
add(o(22.47), click(), 0.14, "click")
add(piece_out("same")[1] - 0.21, whoosh(0.24, 1200, 500, peak=0.35), 0.065, "whoosh-out")
# every drop
add(o(24.66) - W_IN + 0.12, whoosh(0.28, 700, 3600), 0.14, "whoosh")
add(o(26.60), pop(480, 160), 0.13, "pop")
add(o(29.07), pop(540, 170), 0.13, "pop")
add(o(30.29) - 0.02, pop(620, 190, 0.06), 0.075, "pop")   # in the cut before "und alles andere", never on the words
# no exit whoosh here: together with the QR whoosh and pop it crowded the borderline word "joint" (measured)
# QR + House of Lavish
add(o(31.96) - W_IN + 0.10, whoosh(0.30, 400, 2400), 0.07, "whoosh")
add(o(31.96) + 0.27, pop(340, 120, 0.10), 0.055, "pop")
add(o(33.60) + 0.02, click(), 0.06, "click")
# logo card
add(TOTAL - 0.02, impact(1.25, 84, 38), 0.21, "impact-logo")

pk = np.abs(bus).max()
print("sfx peak %.3f, cues %d" % (pk, len(cues)))
with wave.open(J + "/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(bus, -1, 1) * 32767).astype("<i2").tobytes())
json.dump(sorted(cues), open(J + "/sfx_cues.json", "w"))
