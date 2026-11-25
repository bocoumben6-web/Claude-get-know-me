# Video "Beanie Lavish Week" (IMG_4824 + Riem_Arcaden_2 mic, +12.78 s). Rule 25.11.: Lavish pants regularly in full view.
P = [
 (18.48, 19.45, "dbl"),   # Die Beanie Lavish Week.
 (20.50, 21.80, "p1"),    # ein Beanie 30
 (21.82, 23.10, "p2"),    # zwei Beanies 50
 (23.15, 24.60, "p3"),    # drei Beanies kriegt ihr für 60
 (25.98, 29.40, "web"),   # Wir werden Bundles auf unserer Website natürlich noch dementsprechend anpassen.
 (29.62, 34.20, "aus"),   # Ihr könnt euch selber aussuchen, welche Beanie ihr mit welcher Beanie haben wollt.
 (39.70, 41.75, "rockt"), # dann rockt mal alle die Beanie
 (42.50, 43.55, "out"),   # Lavish Owner is out
]
SUBS = [
 (18.50, 19.42, "DIE *BEANIE LAVISH WEEK*"),
 (20.55, 21.76, "EINE BEANIE *30*"),
 (21.86, 23.05, "ZWEI BEANIES *50*"),
 (23.18, 24.55, "DREI BEANIES KRIEGT IHR FÜR *60*"),
 (26.00, 27.60, "WIR WERDEN *BUNDLES* AUF UNSEREN WEBSITES"),
 (27.62, 29.30, "NATÜRLICH NOCH DEMENTSPRECHEND ANPASSEN"),
 (29.65, 31.50, "IHR KÖNNT EUCH SELBER *AUSSUCHEN*"),
 (31.52, 32.92, "WELCHE BEANIE IHR MIT"),
 (32.94, 34.15, "WELCHER *BEANIE* HABEN WOLLT"),
 (39.72, 41.70, "DANN *ROCKT* MAL ALLE DIE BEANIE"),
 (42.55, 43.52, "*LAVISH OWNER* IS OUT"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (36.40, 37.30)
NOISE = (36.40, 0.90)
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
