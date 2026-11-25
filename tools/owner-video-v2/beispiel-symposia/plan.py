# Video "Symposia" (IMG_4826 + Riem_Arcaden_4 mic, +2.05 s). Retention: question hook, ~21 s, date as graphic, short logo.
P = [  # (src_start, src_end, name)
 (2.05, 4.20, "q"),       # Was ist eigentlich Symposia?
 (5.55, 8.91, "fr"),      # Diesen Freitag wird Lavish bei Symposia dabei sein.
 (10.75, 13.73, "ort"),   # Es ist ein Ort, an dem viele Creatives zusammenkommen.
 (15.28, 18.02, "djs"),   # DJs, Künstler,
 (19.62, 20.60, "tanz"),  # sogar Tanz,
 (21.98, 23.19, "aus"),   # Ausdruckstanz.
 (29.15, 30.08, "komf"),  # ich möchte mal außerhalb
 (30.62, 32.32, "komf2"), # von meiner Komfortzone
 (38.07, 39.65, "sehen"), # und möchte sehen,
 (40.50, 42.05, "wirken"),# wie diese Leute auf Lavish wirken.
 (50.70, 52.20, "mal"),   # Und mal schauen, was da geht
 (52.35, 54.04, "out"),   # Lavish Owner is out
]
SUBS = [  # (src_start, src_end, text) ; *keyword*
 (2.05, 3.95, "WAS IST EIGENTLICH *SYMPOSIA*"),
 (5.60, 6.60, "DIESEN *FREITAG*"),
 (6.62, 8.70, "WIRD LAVISH BEI *SYMPOSIA* DABEI SEIN"),
 (10.78, 12.10, "ES IST EIN ORT AN DEM"),
 (12.12, 13.62, "VIELE *CREATIVES* ZUSAMMENKOMMEN"),
 (15.35, 17.85, "*DJS* KÜNSTLER"),
 (19.62, 20.55, "SOGAR *TANZ*"),
 (21.98, 23.02, "*AUSDRUCKSTANZ*"),
 (29.17, 30.05, "HEY ICH MÖCHTE MAL"),
 (30.68, 32.10, "AUSSERHALB VON MEINER *KOMFORTZONE*"),
 (38.09, 39.62, "UND MÖCHTE SEHEN WIE"),
 (40.50, 42.00, "DIESE LEUTE AUF *LAVISH* WIRKEN"),
 (50.75, 52.15, "MAL SCHAUEN WAS DA GEHT"),
 (52.40, 53.75, "*LAVISH OWNER* IS OUT"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (23.30, 24.20)
NOISE = (23.30, 0.90)
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
