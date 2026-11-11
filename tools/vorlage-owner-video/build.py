import json, subprocess, re
HL = r"{\c&HE4F0FC&\fscx135\fscy135\t(0,140,\fscx112\fscy112)}\1{\r}"  # keyword: beige #FCF0E4, pop

E = "/tmp/claude-0/-home-user-Claude-get-know-me/f7c208d9-cfe9-5c5e-b03e-8799bfe7cf57/scratchpad/edit"
FONTS = "/home/user/Claude-get-know-me/assets/fonts"
words = json.load(open(E + "/words.json"))

def wt(word, after, end=False):
    """time of first word matching `word` starting at/after `after`"""
    for w in words:
        if w["s"] >= after - 0.05 and word.lower() in w["w"].lower():
            return w["e"] if end else w["s"]
    raise KeyError(word)

# (source_start, source_end, corrected text, zoom)
C = []
def add(s, e, text, z): C.append([s, e, text, z])
add(0.00, 1.92, "WARUM WIRD DIE WEBSITE ÜBERHAUPT NEU GEMACHT", 1.00)
add(2.26, 3.10, "GANZ EINFACH", 1.12)
l2 = wt("Lavish", 4.7)
add(3.58, l2 - 0.05, "LAVISH IST *GRÖSSER* GEWORDEN", 1.12)
add(l2, 6.78, "LAVISH HAT 1 *ANDERES LEVEL* MITTLERWEILE", 1.00)
add(7.50, 9.82, "DEMENTSPRECHEND MUSS DIE WEBSITE NATÜRLICH AUCH SO AUSSEHEN", 1.00)
add(10.08, 11.10, "SIE MUSS *FIRE* SEIN", 1.25)
add(11.38, 13.54, "GENAUSO WIE MEINE PIECES GENAUSO WIE ICH ES BIN", 1.00)
add(13.80, 15.34, "GENAUSO WIE DIE LEUTE DIE LAVISH ROCKEN", 1.00)
add(15.66, 17.10, "VERSTEHST DU SIE MUSS *SWAG* HABEN", 1.18)
add(17.96, 19.74, "ICH WEISS NOCH BACK IN THE DAYS", 1.00)
add(19.92, 21.64, "ALS ICH DIE WEBSITE *GANZ ALLEINE* GEMACHT HAB", 1.00)
v = wt("von", 21.8)
add(21.80, v - 0.05, "UND ICH HAB ÜBERHAUPT *GAR KEINE AHNUNG*", 1.12)
add(v, 24.72, "VON DIESEM E-COMMERCE GEHABT", 1.12)
add(25.10, 26.62, "UND ICH HAB MEIN BESTES VERSUCHT", 1.00)
add(27.02, 28.50, "UND ICH HAB AUCH *SALES* DADURCH GENERIERT", 1.00)
add(28.50, 31.64, "ABER WIR WOLLEN NE *STÄNDIGE STEIGERUNG* WISST IHR", 1.15)
wn = wt("wenn", 32.0)
add(32.02, wn - 0.05, "WEIL AM ENDE DES TAGES", 1.00)
add(wn, 34.28, "WENN WIR LAVISH ERLEBEN WOLLEN", 1.00)
add(34.94, 36.84, "MÜSSEN WIR BIS NACH *GANZ NACH OBEN*", 1.22)
add(37.78, 40.08, "JA MANN DESWEGEN *SEID GESPANNT*", 1.00)
u = wt("und", 41.0)
add(40.58, u - 0.05, "ICH FREU MICH", 1.12)
add(u, 44.70, "UND *DANKE* FÜR JEDEN DER MICH BIS JETZT SUPPORTET HAT", 1.00)

# pieces: pad chunk edges, keep small gaps (<0.35 s), cut bigger pauses
PAD_IN, PAD_OUT, GAP = 0.10, 0.14, 0.35
pieces = []
for i, (s, e, txt, z) in enumerate(C):
    ps = 0.0 if i == 0 else max(s - PAD_IN, pieces[-1][1])
    if i > 0 and s - C[i - 1][1] < GAP:
        ps = pieces[-1][1]
    if i + 1 < len(C) and C[i + 1][0] - e < GAP:
        pe = C[i + 1][0] - (0 if C[i + 1][0] - e < GAP else PAD_IN)
    else:
        pe = e + PAD_OUT if i + 1 == len(C) else min(e + PAD_OUT, C[i + 1][0] - PAD_IN)
    pieces.append([round(ps, 3), round(pe, 3), z, s, e, txt])

# filter graph
fr = 1 / 30
lines, cat = [], []
for k, (ps, pe, z, *_ ) in enumerate(pieces):
    w = int(round(1080 / z / 2) * 2); h = int(round(1920 / z / 2) * 2)
    x = (1080 - w) // 2
    y = int(1920 * 0.64 * (1 - 1 / z))          # keep the subtitle band in place
    y = min(max(0, y), 1920 - h)
    lines.append(f"[0:v]trim=start={ps}:end={pe},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1[v{k}]")
    d = pe - ps
    lines.append(f"[1:a]atrim=start={ps}:end={pe},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0,d-0.018):.3f}:d=0.018[a{k}]")
    cat.append(f"[v{k}][a{k}]")
lines.append("".join(cat) + f"concat=n={len(pieces)}:v=1:a=1[vc][ac]")
open(E + "/graph.txt", "w").write(";\n".join(lines))

# subtitles on the new timeline
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       # #F0CC38 -> &H0038CCF0 ; shadow black ~35% transparent
       "Style: Sub,Bebas Neue,54,&H0038CCF0,&H0038CCF0,&H00000000,&H59000000,0,0,0,0,100,100,0.5,0,1,0,3,8,170,170,0,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
t = 0.0
for ps, pe, z, s, e, txt in pieces:
    a = t + max(0, s - ps) - 0.03
    b = t + (pe - ps)
    ass.append(f"Dialogue: 0,{ts(max(0,a))},{ts(b)},Sub,,0,0,0,,{{\\an8\\pos(540,1186)}}" + re.sub(r"\*(.+?)\*", lambda m: HL.replace("\\1", m.group(1)), txt))
    t += pe - ps
open(E + "/subs.ass", "w").write("\n".join(ass) + "\n")
json.dump(pieces, open(E + "/pieces.json", "w"), ensure_ascii=False)
print(f"pieces={len(pieces)} new_duration={t:.2f}s")
for p in pieces: print(f"{p[0]:6.2f}-{p[1]:6.2f} z={p[2]:.2f} {p[5]}")
