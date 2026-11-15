"""Prüft jeden Sound gegen die Sprache: während gesprochen wird mind. 9 dB leiser, in Pausen nicht lauter als die Stimme."""
import json, subprocess, numpy as np
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job2"
for src, dst in (("a_speech.wav", "sp.raw"), ("sfx.wav", "sx.raw")):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/" + src, "-f", "f32le", "-ac", "2", "-ar", "48000", J + "/" + dst])
sp = np.fromfile(J + "/sp.raw", dtype=np.float32).reshape(-1, 2).mean(1); sx = np.fromfile(J + "/sx.raw", dtype=np.float32).reshape(-1, 2).mean(1)
n = min(len(sp), len(sx)); sp = sp[:n]; sx = sx[:n]
db = lambda x: float(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9))
speech = float(np.percentile([db(sp[i:i + 2400]) for i in range(0, n - 2400, 2400)], 75))
groups = []
for t, name, g, *_ in json.load(open(J + "/sfx_cues.json")):
    if groups and t - groups[-1][1] < 0.25: groups[-1][1] = t; groups[-1][2].add(name)
    else: groups.append([t, t, {name}])
bad = []
for t0, t1, names in groups:
    a = int(max(0, t0 - 0.02) * 48000); b = int(min(n / 48000, t1 + 0.35) * 48000); best = (-99.0, 0)
    for i in range(a, b - 3840, 960):
        v = db(sx[i:i + 3840])
        if v > best[0]: best = (v, i)
    here = db(sp[best[1]:best[1] + 3840]); talking = here > speech - 10
    if talking and here - best[0] < 9: bad.append([round(t0, 2), "nur %.1f dB unter der Sprache" % (here - best[0])])
    if not talking and best[0] > speech - 2: bad.append([round(t0, 2), "in der Pause lauter als die Stimme"])
print("SOUNDS: %d Stellen, Sprache typisch %.1f dBFS" % (len(groups), speech))
print("  [%s] jeder Sound mind. 9 dB unter der Sprache bzw. in Pausen leiser als die Stimme %s" % ("OK " if not bad else "FEHLER", bad if bad else ""))
json.dump({"ok": not bad, "bad": bad, "stellen": len(groups)}, open(J + "/sfx_check.json", "w"))
