# Video "Black Friday = Beanies" (IMG_4822 + Riem_Arcaden mic, +3.55 s)
P = [  # (src_start, src_end, name)
 (7.78, 9.43, "hook"),    # was bringt zu Black Friday raus?
 (14.45, 15.50, "bean"),  # Wir gehen mit Beanies.
 (17.98, 22.42, "col"),   # Es werden drei neue Colorways kommen, beziehungsweise zwei neue Colorways, ein Restock.
 (25.00, 29.05, "camo"),  # Ja, ihr wolltet alle die Camo Beanie? Also kriegt ihr die Camo Beanie.
 (29.50, 31.07, "out"),   # Lavish Owner is out
]
SUBS = [
 (7.80, 9.20, "WAS BRING ICH ZU *BLACK FRIDAY* RAUS"),
 (14.50, 15.36, "WIR GEHEN MIT *BEANIES*"),
 (18.02, 19.42, "ES WERDEN *DREI* NEUE COLORWAYS KOMMEN"),
 (19.62, 21.18, "BEZIEHUNGSWEISE *ZWEI* NEUE COLORWAYS"),
 (21.58, 22.30, "EIN *RESTOCK*"),
 (25.05, 27.06, "JA IHR WOLLTET ALLE DIE *CAMO BEANIE*"),
 (27.34, 29.03, "ALSO KRIEGT IHR DIE *CAMO BEANIE*"),
 (29.53, 30.72, "*LAVISH OWNER* IS OUT"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (23.00, 23.90)
NOISE = (23.00, 0.90)
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
