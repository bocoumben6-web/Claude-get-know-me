# Video "1 gegen 1 Turnier" (IMG_4827 + Riem_Arcaden_5 mic, +4.81 s). Teaser; unclear last sentence ("das wird die Zeit/Welt …") cut.
P = [
 (5.50, 9.96, "s1"),       # Wir wären ja nicht Lavish, wenn wir nicht noch irgendwelche Sachen planen würden.
 (10.02, 11.62, "vogel1"), # Also ein Vogel hat mir gezwitschert,
 (11.68, 15.76, "vogel2"), # dass es wahrscheinlich was mit Fußball zu tun hat und vielleicht auch
 (16.18, 20.78, "turnier"),# mehr oder weniger ein 1 gegen 1 Turnier. Ich weiß nicht von wem, ich weiß nicht wann,
 (29.32, 31.44, "vert"),   # Und wie wir dort vertreten sein werden
 (37.10, 38.76, "out"),    # Lavish Owner is out
]
SUBS = [
 (5.56, 7.40, "WIR WÄREN JA NICHT *LAVISH*"),
 (7.42, 8.28, "WENN WIR NICHT NOCH"),
 (8.30, 9.92, "IRGENDWELCHE SACHEN *PLANEN* WÜRDEN"),
 (10.06, 11.58, "ALSO EIN *VOGEL* HAT MIR ZUGEZWITSCHERT"),
 (11.72, 14.45, "DASS ES WAHRSCHEINLICH WAS MIT *FUSSBALL* ZU TUN HAT"),
 (14.47, 15.72, "UND VIELLEICHT AUCH"),
 (16.22, 18.40, "MEHR ODER WENIGER EIN *1 GEGEN 1 TURNIER*"),
 (18.42, 19.72, "ICH WEISS NICHT VON *WEM*"),
 (19.74, 20.74, "ICH WEISS NICHT *WANN*"),
 (29.36, 31.40, "UND WIE WIR DORT *VERTRETEN* SEIN WERDEN"),
 (37.14, 38.72, "*LAVISH OWNER* IS OUT"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (26.30, 27.20)
NOISE = (27.30, 0.90)
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
