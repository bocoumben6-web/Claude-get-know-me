# shared edit plan (source times on master.mkv) – Black Friday / Beanie-Deal
P = [  # (src_start, src_end, name)
 (0.12, 1.86, "q1"),        # Was machen wir zu Black Friday?
 (1.90, 3.00, "q2"),        # Was bringen wir raus zu Black Friday?
 (3.62, 4.80, "ahnung"),    # Ich hab absolut keine Ahnung
 (5.02, 5.92, "ueber"),     # Überfragt  (+ air: topic change)
 (7.10, 8.86, "aktion"),    # Ich weiß nicht, ob eine Aktion kommen wird (+ air)
 (9.44, 10.24, "glueck"),   # Wenn ich Glück hab, (in context; isolated it sounds like "ihr ... habt")
 (12.44, 14.62, "beanies"), # werd ich irgendwas mit Beanies machen, aber sonst... (+ air: trailing off)
 (14.78, 15.80, "ah"),      # Ah!
 (16.95, 18.78, "helfen"),  # Ihr müsst mir auf jeden Fall helfen, ja?
]
SUBS = [  # (src_start, src_end, text) ; *keyword*
 (0.26, 1.73, "WAS MACHEN WIR ZU *BLACK FRIDAY*"),
 (2.00, 2.87, "WAS BRINGEN WIR RAUS ZU *BLACK FRIDAY*"),
 (3.76, 4.69, "ICH HAB *ABSOLUT KEINE AHNUNG*"),
 (5.13, 5.55, "ÜBERFRAGT"),
 (7.22, 8.49, "ICH WEISS NICHT OB EINE *AKTION* KOMMEN WIRD"),
 (9.57, 10.12, "WENN ICH GLÜCK HAB"),
 (12.56, 14.24, "WERD ICH IRGENDWAS MIT *BEANIES* MACHEN ABER SONST"),
 (17.08, 18.54, "IHR MÜSST MIR AUF JEDEN FALL *HELFEN* JA"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 2.2             # end card length (logo only)
TONE = (10.70, 11.90)  # room tone (quiet pause in the source) under the end card
NOISE = (10.70, 1.20)  # (start, length) on master.mkv: clean pause used as noise profile for voice.py
def out_time(t):
    off = 0.0
    for s, e, _ in P:
        if s <= t <= e: return off + t - s
        if t < s: return off
        off += e - s
    return off
def piece_out(name):
    off = 0.0
    for s, e, n in P:
        if n == name: return off, off + e - s
        off += e - s
    raise KeyError(name)
TOTAL = sum(e - s for s, e, _ in P)
