"""Shared: how many subtitle words do three recognisers understand in an audio file (decoded through AAC, like the finished video)?
One recogniser alone flips on borderline words; three together are stable enough to judge a mix."""
import sys, subprocess, re, difflib, numpy as np
from faster_whisper import WhisperModel
J = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/job14"
sys.path.insert(0, J)
from plan import SUBS
try:
    from plan import SUBS_HEAR as SUBS
except ImportError:
    pass
_models = None
def models():
    global _models
    if _models is None: _models = [WhisperModel(n, device="cpu", compute_type="int8") for n in ("large-v3", "medium", "small")]
    return _models
def norm(t):
    t = re.sub(r"[^a-zäöüß0-9 ]", "", t.lower().replace("-", " ").replace("%", " prozent"))
    for a, b in (("pop up", "popup"), ("die selbe", "dieselbe")): t = t.replace(a, b)
    t = re.sub(r"\bflanel(?=\b|muster)", "flanell", t).replace("flanell muster", "flanellmuster").replace("fashion", "fashion")   # spelling variants of the recognisers
    return t.split()
U = norm(" ".join(t.replace("*", "") for _, _, t in SUBS))
def hear(path, through_aac=True):
    """returns (votes per subtitle word 0..3, list of the three raw transcripts)"""
    src = path
    if through_aac:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vn", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", J + "/t/h.m4a"]); src = J + "/t/h.m4a"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-f", "f32le", "-ac", "2", "-ar", "16000", J + "/t/h.raw"])
    au = np.fromfile(J + "/t/h.raw", dtype=np.float32).reshape(-1, 2).mean(1)
    votes = np.zeros(len(U), int); texts = []
    for m in models():
        r, _ = m.transcribe(au, language="de", beam_size=5, condition_on_previous_text=False)
        t = " ".join(s.text.strip() for s in r); texts.append(t); h = norm(t)
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, h, U).get_opcodes():
            if tag == "equal": votes[j1:j2] += 1
    return votes, texts
