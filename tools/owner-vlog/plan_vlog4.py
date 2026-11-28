"""Vlog 4 (Express-Lieferungen, 27.11.2026). Sprach-Bereiche werden automatisch von Pausen > 0,45 s befreit."""
import os, numpy as np, scipy.io.wavfile as _w
JOB = os.environ.get("JOB", "/tmp/claude-0/-home-user-Claude-get-know-me/019e819c-46ae-555e-8d8d-6adb89d74114/scratchpad/vlog4")
CLIPS = JOB + "/clips"
OUTNAME = "vlog4_v1.mp4"

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
    *V("4949", 0.0, 5.3),        # So, wir machen jetzt die erste Express-Lieferung, Andi ist am Steuer.
    *V("4949", 6.4, 7.3),        # Moin!
    "SWITCH",
    *V("4950", 0.0, 13.2),       # Expresslieferung. Joel, stell dich mal vor ... gut für Dates und so.
    *V("4950", 16.8, 17.8),      # Schönes Ambiente.
    "SWITCH",
    *V("4953", 0.0, 2.7),        # Halbzeit. Wir gehen jetzt natürlich ... essen. (quer gedreht)
    ("4954", 2.3, 4.1, "music"), # Spaß auf der Straße
    ("4957", 1.2, 3.0, "music"), # Essen
    ("4958", 3.0, 5.0, "music"), # Auto, Lachen
    *V("4959", 0.0, 3.3),        # Ich bin kaputt
    *V("4962", 0.0, 2.0),        # Expresslieferung, ne? (quer gedreht)
    "SWITCH",
    *V("4965", 0.0, 22.6),       # Roomtour: Lernen, Bett, Sofa, Schminktisch
    "SWITCH",
    *V("4970", 0.2, 9.3),        # So, das sind die fertigen Haare ... ist echt saftig.
    ("4971", 0.0, 2.0, "music"), # Parkhaus, Schluss
]
SWITCH_LEN = 0.4
ROTATE = {"4953": "transpose=2", "4962": "transpose=2"}
PORTRAIT = set()
NOISE = {}
SUBS = None
PROMPT = "Vlog. Express-Lieferung, Andi, Joel, Lavish, Roomtour."
FIX = {"levish": "Lavish", "espresslieferung": "Expresslieferung", "festlieferung": "Expresslieferung"}
DROP = []
REPLACE = [
    ("EXPRESS -LIEFERUNGEN", "EXPRESS-LIEFERUNGEN"),
    ("EXPRESS -LIEFERUNG", "EXPRESS-LIEFERUNG"),
    ("EXPRESS -LIEFERUNG", "EXPRESS-LIEFERUNG"),
    ("BYE", "MOIN"),
    ("VERSTEHST DU VERSTEHST DU", "VERSTEHST DU"),
    ("AUCH GUTE FÜR", "AUCH GUT FÜR"),
    ("CHAUVIN -RE -ESSEN", "ESSEN"),
    ("WILLST DU EIN BISSCHEN BESUCHEN", "WENN DU EIN MÄDCHEN BESUCHST"),
    ("MAX", "MAGST"),
    ("SAFE -SAFT", "SAFTIG"),
]
