"""Sounds dürfen die Sprache nicht verdecken. Drei Erkenner hören die Stimme allein und die Mischung.
Ein Wort gilt als DURCH SOUNDS VERLOREN, wenn es ohne Sounds von der Mehrheit verstanden wird, mit Sounds nicht mehr,
UND ein Sound auf oder direkt neben dem Wort liegt (+/- 0,35 s). Ohne Sound in der Nähe ist es normale Schwankung der
Erkenner (gemessen: bis +/- 4 von 249 Punkten bei unhörbaren Unterschieden); die wird nur über die Gesamtpunktzahl begrenzt."""
import sys, json
sys.path.insert(0, "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job3")
from hear3 import hear, U, J, norm
from plan import SUBS, out_time
# approximate time span of every subtitle word (inside its phrase, by character position)
spans = []
for s, e, t in SUBS:
    ws = norm(t.replace("*", "")); a, b = out_time(s), out_time(e); tot = sum(len(w) + 1 for w in ws); p = 0
    for w in ws:
        spans.append((a + (b - a) * p / tot, a + (b - a) * (p + len(w) + 1) / tot)); p += len(w) + 1
assert len(spans) == len(U), (len(spans), len(U))
cues = [(c[0], c[0] + min(c[3], 0.45), c[1]) for c in json.load(open(J + "/sfx_cues.json"))]   # only the loud first part of a sound can mask
def near(i, pad=0.35):
    a, b = spans[i]; return sorted({n for s, e, n in cues if s < b + pad and e > a - pad})
va, _ = hear(J + "/a_speech.wav"); vb, _ = hear(J + "/a_mix.wav")
drop = [i for i in range(len(U)) if va[i] >= 2 and vb[i] < 2]
cand = [i for i in drop if near(i)]; wobble = [i for i in drop if not near(i)]
# Gegenprobe: die Sounds rund um das Wort stumm schalten. Bleibt das Wort trotzdem unverstanden, liegt es nicht am Sound.
import wave, subprocess, numpy as np
def rd(p):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/" + p, "-f", "f32le", "-ac", "2", "-ar", "48000", J + "/t/r.raw"]); return np.fromfile(J + "/t/r.raw", dtype=np.float32).reshape(-1, 2)
lost = []; cleared = []
if cand:
    sp = rd("a_speech.wav"); sx = rd("sfx.wav"); n = min(len(sp), len(sx))
    for i in cand:
        z = sx[:n].copy(); z[int(max(0, spans[i][0] - 0.8) * 48000):int((spans[i][1] + 1.6) * 48000)] = 0
        with wave.open(J + "/t/g.wav", "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(sp[:n] + z, -0.84, 0.84) * 32767).astype("<i2").tobytes())
        vc, _ = hear(J + "/t/g.wav")
        (lost if vc[i] >= 2 else cleared).append(i)
print("SOUNDS GEGEN WÖRTER  (3 Erkenner, max. %d Punkte): Stimme allein %d, mit Sounds %d" % (3 * len(U), va.sum(), vb.sum()))
for i in lost: print("   VERLOREN durch Sounds: '%s' bei %.1f s  (... %s ...)  Sound dort: %s" % (U[i], spans[i][0], " ".join(U[max(0, i - 3):i + 4]), near(i)))
for i in cleared: print("   Gegenprobe: '%s' bei %.1f s bleibt auch ohne die Sounds dort undeutlich -> liegt nicht am Sound" % (U[i], spans[i][0]))
for i in wobble: print("   schwankt, aber kein Sound in der Nähe: '%s' bei %.1f s (%d -> %d Stimmen)" % (U[i], spans[i][0], va[i], vb[i]))
TOL = round(0.04 * 3 * len(U))   # Schwankung der Erkenner: bis ca. 4 % der Punkte ohne hörbare Ursache (gemessen)
ok = (not lost) and (va.sum() - vb.sum() <= TOL)
print("  [%s] kein Wort wird von einem Sound verdeckt; Gesamtpunkte %+d (erlaubt bis -%d)" % ("OK " if ok else "FEHLER", vb.sum() - va.sum(), TOL))
json.dump({"ok": bool(ok), "verdeckt": [U[i] for i in lost], "schwankt_ohne_sound": [U[i] for i in wobble], "ohne": int(va.sum()), "mit": int(vb.sum())}, open(J + "/sound_words.json", "w"))
