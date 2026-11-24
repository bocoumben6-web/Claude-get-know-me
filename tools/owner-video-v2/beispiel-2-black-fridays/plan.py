# Video 1 "2 Black Fridays" (Showroom). master.mkv = IMG_4832 (0) + IMG_4833 (17.400) + IMG_4834 (29.367), 9:16 face-follow crop
# Retention: starts with the strongest line, ~17 s, open loop (3 secret cards) -> beanie reveal at the end, short logo.
P = [  # (src_start, src_end, name)
 (7.50, 10.22, "hook"),    # jedes Jahr muss ich immer zwei Black Friday vorbereiten
 (17.40, 21.50, "hier"),   # Wenn ich sage vorbereiten, dann heißt es, ich muss hier BF Sachen machen und ich muss hier | (cut: unclear interjection + unclear sentence)
 (10.80, 12.05, "tough"),  # Das ist echt tough
 (29.37, 30.55, "nur1"),   # Ich würde auch nur einen Black Friday machen
 (36.27, 37.40, "nicht"),  # aber so ist es noch nicht
 (15.05, 17.35, "boy"),    # Boy, it is what it is, bro  (+ quiet tail for the beanie question)
]
SUBS = [  # (src_start, src_end, text) ; *keyword*
 (7.50, 8.80, "JEDES JAHR MUSS ICH IMMER"),
 (8.82, 10.15, "*ZWEI* BLACK FRIDAY VORBEREITEN"),
 (17.40, 18.22, "WENN ICH SAGE *VORBEREITEN*"),
 (18.24, 18.76, "DANN HEISST ES"),
 (18.78, 20.82, "ICH MUSS *HIER* BLACK FRIDAY SACHEN MACHEN"),
 (20.86, 21.46, "UND ICH MUSS *HIER*"),
 (10.85, 11.98, "DAS IST ECHT *TOUGH*"),
 (29.37, 29.78, "ICH WÜRDE AUCH NUR *EINEN*"),
 (29.79, 30.52, "BLACK FRIDAY MACHEN"),
 (36.30, 37.10, "ABER SO IST ES *NOCH NICHT*"),
 (15.10, 16.70, "BOY IT IS WHAT IT IS *BRO*"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (13.55, 14.45)   # quiet pause (4832, between "By God" and "Boy")
NOISE = (13.55, 0.90)
def out_time(t):
    off = 0.0
    for s, e, _ in P:
        if s <= t <= e: return off + t - s
        off += e - s
    raise ValueError(t)
def piece_out(name):
    off = 0.0
    for s, e, n in P:
        if n == name: return off, off + e - s
        off += e - s
    raise KeyError(name)
TOTAL = sum(e - s for s, e, _ in P)
