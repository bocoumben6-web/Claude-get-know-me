"""Vlog 3 (Black Friday im Laden + Haare, 26.11.2026). Sprach-Bereiche werden automatisch von Pausen > 0,45 s befreit."""
import os, numpy as np, scipy.io.wavfile as _w
JOB = os.environ.get("JOB", "/tmp/claude-0/-home-user-Claude-get-know-me/019e819c-46ae-555e-8d8d-6adb89d74114/scratchpad/vlog3")
CLIPS = JOB + "/clips"
OUTNAME = "vlog3_v1.mp4"

def _autocut(c, a, b, min_sil=0.45, keep=0.15):
    """Pausen im Bereich a..b rausnehmen (Schwelle relativ zum Clip), Wortenden bleiben (keep)."""
    sr, x = _w.read(f"{CLIPS}/IMG_{c}.wav"); x = x.astype(np.float32) / 32768
    n = int(sr * 0.02); e = np.array([np.sqrt((x[i:i + n] ** 2).mean()) for i in range(0, len(x) - n, n)])
    d = np.convolve(20 * np.log10(e + 1e-9), np.ones(5) / 5, "same")
    lo, hi = np.percentile(d, 10), np.percentile(d, 90); q = d < lo + 0.3 * (hi - lo)
    segs, cur, i = [], a, int(a / 0.02)
    while i < min(len(q), int(b / 0.02)):
        if q[i]:
            j = i
            while j < len(q) and q[j]: j += 1
            s0, s1 = i * 0.02, min(j * 0.02, b)
            if s1 - s0 >= min_sil and s0 > a + 0.1 and s1 < b - 0.1:
                segs.append((c, round(cur, 2), round(s0 + keep, 2), "voice")); cur = s1 - keep
            i = j
        else: i += 1
    segs.append((c, round(cur, 2), b, "voice"))
    return segs

V = _autocut
SEGMENTS = [
    *V("4905", 0.0, 6.3),        # So, mein Aussehen heute ... Black Friday
    *V("4906", 0.0, 9.9),        # Getränke für die Gäste, Preise machen, mein Kollege Tidi
    *V("4907", 0.0, 7.0),        # Bist du bereit für den Ansturm? (2. Versuch) I was born ready
    *V("4908", 0.0, 8.8),        # bereit für die schönen Frauen? ... Genau meine Mentalität
    *V("4909", 0.0, 2.6),        # Schau dir den an
    ("4910", 0.0, 2.6, "music"), # Laden voll
    ("4914", 1.2, 2.9, "music"), # Gedränge (quer gedreht)
    ("4915", 0.2, 1.3, "voice"), # Ich kann nicht mehr
    *V("4917", 0.0, 1.0), *V("4917", 3.2, 9.0), *V("4917", 10.6, 11.7),   # Wie fühlst du dich? Mir geht's nicht gut
    *V("4918", 0.1, 7.1), *V("4918", 11.4, 13.8),                          # We're done ... Ihr habt uns heute geknallt
    "SWITCH",
    *V("4919", 0.0, 6.2),        # Ich muss noch unbedingt meine Haare machen ... mit dieser Mähne
    ("4920", 0.5, 2.0, "music"), # Autotür (quer gedreht)
    ("4921", 0.2, 1.7, "music"), # Fahrt nachts
    "SWITCH",
    *V("4923", 0.0, 5.4),        # Wir sind jetzt angekommen ... Haare dringend nötig
    *V("4925", 0.6, 2.2),        # Zwischenstand der Haare
    *V("4925", 3.9, 7.5),        # ... Ja, Mann.
]
SWITCH_LEN = 0.4
ROTATE = {"4914": "transpose=2", "4920": "transpose=2", "4924": "transpose=2"}
PORTRAIT = set()
NOISE = {}
SUBS = None
PROMPT = "Vlog. Black Friday, Ansturm, Tidi, Lavish."
FIX = {"levish": "Lavish", "levelstand": "Lavish", "red": "Bruder"}
DROP = []
REPLACE = []
