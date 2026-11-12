# shared edit plan (source times on master.mkv)
P = [  # (src_start, src_end, name)
 (0.54, 2.70, "hook1"), (3.72, 4.88, "hook2"), (5.48, 6.48, "erklaer"), (7.70, 9.76, "website"),
 (10.62, 14.96, "walink"), (15.33, 16.78, "early"),
 (17.17, 21.95, "sample"),   # Sample Review + pop-up run uncut, with air after "10 Sekunden" (owner: cut came too fast)
 (22.25, 23.30, "same"),
 (23.73, 25.36, "drop"),     # "...neuen Drop habe" | pause + restart removed (owner: sounded doubled)
 (26.17, 27.42, "drop2"),    # "werde ich da Verlosungen"
 (28.98, 29.76, "disc"), (30.28, 31.53, "alles"),
 (31.70, 35.03, "join"),     # last sentence runs uncut (the word "Gruppe" ends at 32.86)
]
SUBS = [  # (src_start, src_end, text) ; *keyword*
 (0.66, 2.60, "WIE HABT IHR DIE MÖGLICHKEIT *15 PROZENT*"),
 (3.80, 4.80, "*DISCOUNT* ZU BEKOMMEN"),
 (5.58, 6.40, "DAS ERKLÄRE ICH EUCH JETZT"),
 (7.80, 9.70, "WIR HABEN JETZT NATÜRLICH EINE *NEUE WEBSITE*"),
 (10.70, 13.55, "UND OBEN STEHT DIREKT DER *WHATSAPP-LINK*"),
 (13.72, 14.86, "KOMMT IN DIE *WHATSAPP-GRUPPE* REIN"),
 (15.40, 16.70, "*15 PROZENT* EARLY ACCESS"),
 (17.24, 18.66, "UND NATÜRLICH AUCH *SAMPLE REVIEW*"),
 (19.25, 21.45, "NATÜRLICH KRIEGT IHR AUCH EIN *POP-UP* NACH 10 SEKUNDEN"),
 (22.45, 23.02, "GENAU DIESELBE GESCHICHTE"),
 (23.80, 25.30, "UND JEDES MAL WENN ICH EINEN *NEUEN DROP* HABE"),
 (26.20, 27.32, "WERDE ICH DA *VERLOSUNGEN*"),
 (29.05, 29.66, "*DISCOUNTS*"),
 (30.35, 31.44, "UND ALLES ANDERE MÖGLICHE REINSCHICKEN"),
 (31.78, 32.92, "ALSO JOINT DER *WHATSAPP-GRUPPE*"),
 (33.58, 34.92, "*HOUSE OF LAVISH*"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 2.2          # end card length (logo + QR)
TONE = (27.40, 28.90)  # room tone (pause in the source) under the end card, fades to silence
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
