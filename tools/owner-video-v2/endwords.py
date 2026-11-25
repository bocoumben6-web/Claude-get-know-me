"""Transcribe the cut audio and show the last words of every piece (to catch clipped endings or fragments of the next word)."""
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
J = sys.argv[1]; sys.path.insert(0, J)
from plan import P
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", J + "/cut_a.wav", "-f", "f32le", "-ac", "1", "-ar", "16000", J + "/t/c16.raw"])
a = np.fromfile(J + "/t/c16.raw", dtype=np.float32)
for k in ("large-v3", "medium"):
    r, _ = WhisperModel(k, device="cpu", compute_type="int8").transcribe(a, language="de", beam_size=5, word_timestamps=True, condition_on_previous_text=False)
    ws = [w for x in r for w in x.words]; off = 0; line = []
    for s, e, n in P:
        d = e - s; inside = [w.word.strip() for w in ws if off - 0.1 <= w.start < off + d - 0.05]
        line.append(f"{n}: …{' '.join(inside[-3:])}"); off += d
    print(k, " | ".join(line))
