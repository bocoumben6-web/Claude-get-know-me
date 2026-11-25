# Video "Genau diese Beanie" (IMG_4825 + Riem_Arcaden_3 mic, +3.38 s). Cuts set on dual-band segments (segs.py).
P = [
 (3.96, 5.50, "h1"),     # Für die meisten Leute
 (6.40, 7.38, "h2a"),    # ist vielleicht
 (7.78, 9.26, "h2b"),    # genau diese Beanie
 (10.32, 11.62, "h3"),   # das, was sie immer haben wollten.
 (12.08, 14.40, "win"),  # Und diesen Winter kommen wir schon wieder mit Beanies.
 (14.98, 18.98, "far"),  # Ein Restock, zwei neue Farben. Einen in Schwarz, einen in Weiß.
 (19.24, 21.26, "trust"),# Und trust me, wenn ich euch sage,
 (21.72, 23.52, "ver1"), # auf die Beanies von Lavish
 (23.62, 25.36, "ver2"), # ist Verlass.
 (26.70, 28.42, "stay"), # stay active und stay woke.
 (28.46, 29.56, "out"),  # Lavish Owner is out
]
SUBS = [
 (4.00, 5.46, "FÜR DIE MEISTEN LEUTE"),
 (6.44, 7.34, "IST VIELLEICHT"),
 (7.82, 9.22, "GENAU *DIESE BEANIE*"),
 (10.36, 11.58, "DAS WAS SIE IMMER HABEN WOLLTEN"),
 (12.12, 13.20, "UND DIESEN *WINTER*"),
 (13.22, 14.36, "KOMMEN WIR SCHON WIEDER MIT *BEANIES*"),
 (15.02, 17.20, "EIN *RESTOCK* ZWEI NEUE FARBEN"),
 (17.28, 18.94, "EINEN IN *SCHWARZ* EINEN IN *WEISS*"),
 (19.28, 21.22, "UND *TRUST ME* WENN ICH EUCH SAGE"),
 (21.76, 23.50, "AUF DIE BEANIES VON *LAVISH*"),
 (23.62, 25.32, "IST *VERLASS*"),
 (26.74, 28.38, "STAY ACTIVE UND *STAY WOKE*"),
 (28.50, 29.52, "*LAVISH OWNER* IS OUT"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (31.0, 31.9)
NOISE = (31.0, 0.90)
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
