# Video "King of Beanies" (IMG_4828 + Riem_Arcaden_6 mic, +7.71 s). 23.5 s: prices + free-shipping info justify > 22 s.
P = [
 (10.24, 12.10, "back"),   # Unsere Beanies sind back.
 (12.64, 13.56, "trust1"), # Trust me.
 (13.92, 16.08, "tough1"), # Wer sagt mir, diese Beanie sieht nicht tough aus?
 (17.94, 19.40, "king1"),  # Bro, Lavish ist King
 (20.12, 21.24, "king2"),  # of Beanies.
 (23.38, 27.36, "drei"),   # Drei Beanies, drei Farben. Camo Restock, weiß, schwarz.
 (35.99, 36.50, "e1"),     # Eine,
 (38.18, 41.24, "e2"),     # 30 Euro. Zwei, 50 Euro. Drei, 60 Euro.
 (41.44, 42.62, "schn"),   # Schnäppchen, Bruder.
 (43.02, 48.24, "wa"),     # Und jeder, der auch noch in der WhatsApp-Gruppe ist, kriegt von mir einen Code für kostenlosen Versand.
 (50.06, 52.06, "out"),    # Lavish Owner is out
]
SUBS = [
 (10.28, 12.06, "UNSERE *BEANIES* SIND BACK"),
 (12.68, 13.52, "*TRUST ME*"),
 (13.96, 14.85, "WER SAGT MIR DIESE BEANIE"),
 (14.87, 16.04, "SIEHT NICHT *TOUGH* AUS"),
 (17.98, 19.36, "BRO LAVISH IST"),
 (20.16, 21.20, "*KING OF BEANIES*"),
 (23.42, 24.85, "DREI BEANIES DREI FARBEN"),
 (24.87, 27.32, "*CAMO* RESTOCK WEISS SCHWARZ"),
 (36.02, 36.46, "EINE"),
 (38.22, 39.05, "*30* EURO"),
 (39.07, 40.02, "ZWEI *50* EURO"),
 (40.04, 41.20, "DREI *60* EURO"),
 (41.48, 42.58, "*SCHNÄPPCHEN* BRUDER"),
 (43.06, 45.90, "UND JEDER DER AUCH NOCH IN DER *WHATSAPP-GRUPPE* IST"),
 (46.58, 47.40, "KRIEGT VON MIR EINEN *CODE*"),
 (47.42, 48.20, "FÜR *KOSTENLOSEN VERSAND*"),
 (50.10, 52.02, "*LAVISH OWNER* IS OUT"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (36.70, 37.60)
NOISE = (36.70, 0.90)
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
