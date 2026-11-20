# shared edit plan (video times on master.mkv; audio = separate mic track, synced +0.521 s) – Fitpics / Karussell
P = [  # (src_start, src_end, name)
 (0.00, 3.53, "hook"),     # Meine lieben Damen und Herren, ihr müsst mir einen Gefallen tun
 (4.08, 5.68, "best"),     # Wenn ihr was bestellt bei mir
 (5.86, 6.68, "uns"),      # oder bei uns
 (7.55, 8.74, "post"),     # postet Fitpics   (pause before removed)
 (9.03, 11.88, "sehen"),   # Ich möchte eure Fitpics sehen. Ich möchte die
 (12.13, 14.33, "var"),    # verschiedensten Variationen
 (14.89, 16.82, "pieces"), # mit den Pieces, die ich mache
 (17.36, 21.75, "repost"), # sehen, ich möchte sie reposten, verbreiten, auf meiner Website haben (+ air)
 (22.48, 28.06, "karu"),   # Für die Leute ... ganz unten ist ein Karussell. Da posten wir alle Fitpics rein von allen Kunden, die
 (28.15, 29.18, "lavish"), # Lavish   (1.1 s pause after removed)
 (30.15, 31.80, "rockt"),  # natürlich gerockt haben
 (32.02, 32.72, "also"),   # Also
 (33.15, 37.95, "out"),    # Schickt immer durch und Lavish Owner is out. Ich freu mich auf eure Fitpics. (walks out)
]
SUBS = [  # (src_start, src_end, text) ; *keyword*
 (0.00, 1.62, "MEINE LIEBEN DAMEN UND HERREN"),
 (1.76, 3.41, "IHR MÜSST MIR EINEN *GEFALLEN* TUN"),
 (4.20, 5.56, "WENN IHR WAS *BESTELLT* BEI MIR"),
 (5.97, 6.54, "ODER BEI UNS"),
 (7.67, 8.60, "POSTET *FITPICS*"),
 (9.15, 10.58, "ICH MÖCHTE EURE *FITPICS* SEHEN"),
 (10.63, 11.75, "ICH MÖCHTE DIE"),
 (12.25, 14.21, "VERSCHIEDENSTEN *VARIATIONEN*"),
 (15.01, 16.69, "MIT DEN *PIECES* DIE ICH MACHE"),
 (17.43, 18.75, "SEHEN ICH MÖCHTE SIE *REPOSTEN*"),
 (18.79, 19.95, "ICH MÖCHTE SIE *VERBREITEN*"),
 (20.03, 21.38, "UND ICH MÖCHTE SIE AUF MEINER *WEBSITE* HABEN"),
 (22.55, 23.60, "FÜR DIE LEUTE DIE ES NICHT WISSEN"),
 (23.63, 24.90, "GANZ UNTEN IST EIN *KARUSSELL*"),
 (24.95, 26.70, "DA POSTEN WIR DANN ALLE *FITPICS* REIN"),
 (26.75, 27.95, "VON ALLEN *KUNDEN* DIE"),
 (28.27, 29.06, "*LAVISH*"),
 (30.27, 31.64, "NATÜRLICH *GEROCKT* HABEN"),
 (32.14, 32.60, "ALSO"),
 (33.25, 34.05, "SCHICKT IMMER DURCH"),
 (34.09, 35.30, "UND *LAVISH OWNER* IS OUT"),
 (35.35, 36.89, "ICH FREU MICH AUF EURE *FITPICS*"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 2.2
TONE = (21.50, 22.45)  # quiet pause under the end card
NOISE = (21.50, 0.95)  # clean pause as noise profile (voice.py)
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
