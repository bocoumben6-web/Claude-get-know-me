# shared edit plan (source times on master.mkv) – SNR Flanell
P = [  # (src_start, src_end, name)
 (0.50, 2.76, "hook"),       # Heute reden wir über das SNR Flanell
 (2.94, 4.46, "snr"),        # Still Not Reachable Flanell
 (4.46, 6.42, "beso"),       # Ich erzähle euch die Besonderheiten (continuous with "snr": punch-in only)
 (6.84, 8.06, "saum"),       # Wir haben unten am Saum
 (8.78, 10.26, "dist"),      # mit Distressing gearbeitet
 (10.68, 13.26, "patch"),    # Wir haben drei wunderschöne Patches
 (13.60, 14.40, "pw"),       # Patchworks
 (14.94, 15.56, "nacken"),   # am Nacken
 (16.06, 16.88, "ruecken"),  # auf dem Rücken
 (17.92, 19.36, "seite"),    # an der Seite unten links
 (22.50, 28.26, "muster"),   # Ich meine das Flanell erklärt sich von selber / fünf verschiedene Flanellmuster / wow this is fashion
 (28.50, 30.74, "art"),      # this is art at this point
 (33.70, 35.58, "fit"),      # Und vom Fit wollen wir gar nicht sprechen
 (35.80, 38.08, "rockt"),    # Also wer das nicht rockt
 (39.12, 40.54, "ahnung"),   # hat keine Ahnung Mann (+ a little air before the logo)
]
SUBS = [  # (src_start, src_end, text) ; *keyword*
 (0.62, 2.65, "HEUTE REDEN WIR ÜBER DAS *SNR FLANELL*"),
 (3.04, 4.32, "*STILL NOT REACHABLE* FLANELL"),
 (4.61, 6.28, "ICH ERZÄHLE EUCH DIE *BESONDERHEITEN*"),
 (6.95, 7.93, "WIR HABEN UNTEN AM *SAUM*"),
 (8.89, 10.13, "MIT *DISTRESSING* GEARBEITET"),
 (10.80, 13.13, "WIR HABEN DREI WUNDERSCHÖNE *PATCHES*"),
 (13.71, 14.28, "PATCHWORKS"),
 (15.05, 15.41, "AM *NACKEN*"),
 (16.18, 16.75, "AUF DEM *RÜCKEN*"),
 (18.02, 19.21, "AN DER *SEITE* UNTEN LINKS"),
 (22.62, 24.74, "ICH MEINE DAS FLANELL ERKLÄRT SICH VON SELBER"),
 (24.84, 26.80, "*FÜNF* VERSCHIEDENE FLANELLMUSTER"),
 (26.92, 28.14, "WOW THIS IS *FASHION*"),
 (28.61, 30.60, "THIS IS *ART* AT THIS POINT"),
 (33.81, 35.45, "UND VOM *FIT* WOLLEN WIR GAR NICHT SPRECHEN"),
 (35.91, 37.96, "ALSO WER DAS NICHT *ROCKT*"),
 (39.23, 40.23, "HAT *KEINE AHNUNG* MANN"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 2.2             # end card length (logo only)
TONE = (19.90, 21.40)  # room tone (pause in the source) under the end card, fades to silence
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
