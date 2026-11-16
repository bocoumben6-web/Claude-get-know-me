"""Maßstab für qa.py: wie verständlich ist die Rohaufnahme (nur Tiefen entfernt)?
Die Erkenner schwanken bei Grenzwörtern schon durch unhörbare Unterschiede. Deshalb wird die Rohaufnahme dreimal leicht
verschieden gehört (Pegel, mit/ohne AAC) und pro Wort der NIEDRIGSTE Wert gespeichert: "roh klar" heißt klar in allen drei Läufen."""
import sys, subprocess, json, numpy as np
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job3"
sys.path.insert(0, J)
from hear3 import hear, U
runs = []
for gain, aac in ((12, True), (9, True), (12, False)):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/cut_a.wav", "-af", f"highpass=f=75,volume={gain}dB", J + "/t/rawhp.wav"])
    v, t = hear(J + "/t/rawhp.wav", through_aac=aac); runs.append(v); print("  Lauf: %d Punkte" % v.sum())
v = np.minimum.reduce(runs); json.dump([int(x) for x in v], open(J + "/raw_votes.json", "w"))
print("Rohaufnahme (sicherer Wert): %d von %d Punkten" % (v.sum(), 3 * len(U))); print("  nicht in allen Läufen klar:", [U[i] for i in range(len(U)) if v[i] < 2])
