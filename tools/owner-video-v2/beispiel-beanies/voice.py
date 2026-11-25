"""Voice clean-up for Lavish owner videos. Settings measured on the WhatsApp video (Nov 2026) with three speech recognisers:
high-pass 75 Hz -> profile-based noise reduction 70 % (noise profile = room tone from a speech pause)
-> gentle pause reduction 6 dB (only real pauses; word endings are held).
Result there: distance voice/noise 13.0 -> 19.8 dB, and every word that is clear in the raw recording stays clear.
Do NOT go stronger without re-measuring: 85 % and more, a hard expander, or ffmpeg afftdn all cost words.
Reads cut_a.wav, writes a_voice.wav (48 kHz, dual mono)."""
import sys, subprocess, wave, numpy as np
import noisereduce as nr
from scipy.signal import butter, sosfiltfilt
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job8"
sys.path.insert(0, J)
from plan import TOTAL
try:
    from plan import NOISE
except ImportError:
    NOISE = None
SR = 48000; STRENGTH = 0.55; PAUSE_DB = 6.0   # clean mic take: gentler denoise so endings survive
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/cut_a.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), J + "/t/c.raw"])
raw = np.fromfile(J + "/t/c.raw", dtype=np.float32).astype(np.float64)
hp = lambda x, f: sosfiltfilt(butter(2, f, "hp", fs=SR, output="sos"), x)
db = lambda v: 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-12)
def distance(x):
    x = x[:int(TOTAL * SR)]; w = np.array([db(x[i:i + 2400]) for i in range(0, len(x) - 2400, 1200)])
    return np.percentile(w, 80) - np.percentile(w, 6)
def expander(x, depth_db, hold=0.12):
    """only real pauses get quieter: anything within 7 dB of the noise floor, and never within `hold` s after speech"""
    n = 480; e = np.sqrt(np.convolve(x ** 2, np.ones(n) / n, mode="same")) + 1e-9; d = 20 * np.log10(e); lo = np.percentile(d, 8)
    k = np.clip((d - (lo + 1.5)) / 5.5, 0, 1)
    k = np.maximum.reduce([np.roll(k, s) for s in range(0, int(hold * SR), 480)])     # hold after speech (word tails stay)
    k = np.maximum(k, np.roll(k, -int(0.03 * SR)))                                    # open slightly before a word
    g = 10 ** (-(1 - k) * depth_db / 20); w = int(0.04 * SR)
    return x * np.convolve(g, np.hanning(w) / np.hanning(w).sum(), mode="same")
x0 = hp(raw, 75)
if NOISE:   # clean pause taken straight from the master (best profile; the end-card tone may contain breath)
    _m = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(NOISE[0]), "-t", str(NOISE[1]), "-i", J + "/master.mkv", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    noise = hp(np.frombuffer(_m, dtype=np.float32).astype(np.float64), 75)
else:
    noise = x0[int((TOTAL + 0.15) * SR):int((TOTAL + 1.2) * SR)]          # room tone that sits under the end card
x = nr.reduce_noise(y=x0, sr=SR, y_noise=noise, stationary=True, prop_decrease=STRENGTH, n_fft=2048)[:len(raw)]
x = expander(x, PAUSE_DB)
with wave.open(J + "/a_voice.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
    v = (np.clip(np.stack([x, x], 1), -1, 1) * 8388607).astype("<i4"); w.writeframes(v.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
print("Abstand Stimme/Rauschen: vorher %.1f dB, nachher %.1f dB" % (distance(x0), distance(x)))
