"""Vlog 2 (Arbeitstag + Black Friday, 24.11.2026). Untertitel automatisch aus der geschnittenen Stimme (SUBS = None)."""
import os
JOB = os.environ.get("JOB", "/tmp/claude-0/-home-user-Claude-get-know-me/019e819c-46ae-555e-8d8d-6adb89d74114/scratchpad/vlog2")
CLIPS = JOB + "/clips"
OUTNAME = "vlog2_v1.mp4"

SEGMENTS = [
    # Morgen im Bad
    ("4815", 0.10, 3.98, "voice"),    # Guten Morgen, es ist relativ früh und
    ("4815", 4.48, 8.15, "voice"),    # ich hab heute Arbeit, aber ich muss auch noch Content drehen.
    ("4815", 8.30, 9.40, "voice"),    # Das heißt, jetzt
    ("4815", 12.55, 18.62, "voice"),  # bevor ich arbeiten gehe ... für Lavish natürlich.
    ("4815", 19.12, 27.35, "voice"),  # Oder was weiß ich ... Muss man halt früher aufstehen, ne?
    ("4816", 21.50, 23.70, "music"),  # Tanz/Flex im Bad (Musik lief im Original)
    "SWITCH",
    ("4818", 0.00, 1.23, "music"),    # Straße
    ("4819", 0.00, 8.20, "voice"),    # auf dem Weg zur Garage, Weihnachtsmarkt dort hinten
    "SWITCH",
    # Laden / Black Friday
    ("4832", 0.25, 2.75, "voice"),    # Für die, die es nicht wissen,
    ("4832", 3.65, 11.95, "voice"),   # ich bin noch bei ... arbeiten ... zwei Black Friday vorbereiten. Das ist echt tough.
    ("4833", 0.00, 7.85, "voice"),    # Wenn ich sage vorbereiten ... hier ... und hier ...
    ("4834", 0.00, 1.18, "voice"),    # Ich will doch nur einen Black Friday machen,
    ("4834", 6.86, 7.68, "voice"),    # aber so ist es noch nicht.
    # Lager
    ("4835", 0.20, 1.60, "music"),
    ("4836", 0.00, 1.37, "music"),
    ("4838", 0.30, 1.80, "music"),
    ("4839", 3.00, 4.45, "voice"),    # Super,
    ("4839", 4.98, 8.20, "voice"),    # das haben wir toll gemacht. Die ganze Kartonzeit hier.
    ("4840", 0.00, 3.50, "voice"),    # Also ich bin so 15 Uhr gekommen ...
    ("4840", 4.55, 10.98, "voice"),   # ... die Frauen heute, boah, die haben gar keinen Bock.
    ("4837", 0.00, 0.42, "music"),    # Lach-Reaktion
    "SWITCH",
    # Abends zu Hause
    ("4843", 0.20, 1.42, "voice"),    # Also,
    ("4843", 1.98, 3.75, "voice"),    # ich bin zuhause angekommen
    ("4843", 4.45, 7.00, "voice"),    # und jetzt beginnt es mit After Work,
    ("4843", 8.55, 13.40, "voice"),   # weil ich muss ja auch noch Black Friday für Lavish vorbereiten, so here we go.
    ("4844", 0.90, 2.72, "voice"),    # Und ich muss auch noch ein Video schneiden,
    ("4844", 4.25, 4.65, "voice"),    # ist
    ("4844", 5.50, 6.85, "voice"),    # viel, aber ja.
]
SWITCH_LEN = 0.4
ROTATE = {}
PORTRAIT = set()
NOISE = {"4815": (9.1, 9.8), "4819": (10.7, 11.26), "4832": (2.68, 3.70), "4833": (7.9, 9.2), "4834": (1.58, 2.56),
         "4839": (1.62, 2.6), "4840": (3.5, 4.5), "4843": (6.96, 8.6), "4844": (2.66, 4.3)}
SUBS = None
PROMPT = "Vlog. Lavish, Black Friday, Content, After Work."
FIX = {"levelstand": "Lavish", "lebensstand": "Lavish", "levish": "Lavish", "lewis": "Lavish", "lavis": "Lavish",
       "konzentrieren": "Content drehen"}
DROP = []
