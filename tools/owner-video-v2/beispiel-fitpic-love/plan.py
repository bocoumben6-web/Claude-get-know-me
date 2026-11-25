# Video "Fitpic Love" (IMG_4829 + Riem_Arcaden_7 mic, +5.19 s). Owner not in frame during the first sentence -> customer fitpics open the video.
P = [
 (6.62, 7.82, "q"),       # Wisst ihr, was ich liebe?
 (7.82, 11.42, "love"),   # Ich liebe die Leute, die Lavish rocken und dann dieses Fitpic posten, weil ihr
 (11.80, 13.50, "frisch"),# seid so frisch.
 (13.78, 15.42, "life"),  # On my life. At this point,
 (15.68, 16.38, "ich"),   # ich
 (16.98, 18.94, "spr"),   # spreche einfach nur meine Liebe für euch raus.
 (21.06, 21.80, "peace"), # Peace.
]
SUBS = [
 (6.66, 7.78, "WISST IHR WAS ICH *LIEBE*"),
 (7.86, 9.70, "ICH LIEBE DIE LEUTE DIE *LAVISH* ROCKEN"),
 (9.72, 11.00, "UND DANN DIESES *FITPIC* POSTEN"),
 (11.02, 11.40, "WEIL IHR"),
 (11.84, 13.46, "SEID SO *FRISCH*"),
 (13.82, 14.70, "*ON MY LIFE*"),
 (14.72, 15.38, "AT THIS POINT"),
 (15.72, 17.75, "ICH SPRECHE EINFACH NUR"),
 (17.77, 18.90, "MEINE *LIEBE* FÜR EUCH RAUS"),
 (21.10, 21.76, "*PEACE*"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (23.6, 24.5)
NOISE = (23.6, 0.90)
def out_time(t):
    off = 0.0
    for s, e, _ in P:
        if s - 0.06 <= t <= e + 0.06: return off + min(max(t, s), e) - s
        off += e - s
    raise ValueError(t)
def piece_out(name):
    off = 0.0
    for s, e, n in P:
        if n == name: return off, off + e - s
        off += e - s
    raise KeyError(name)
TOTAL = sum(e - s for s, e, _ in P)
