# Video "WhatsApp-Gruppe in 4 Sprachen" (IMG_4830 + Riem_Arcaden_8 mic, +1.47 s).
# Owner says the same German sentence 4x "auf Englisch / Französisch / Spanisch" (German with accent = the joke).
# Owner 26.11.: all 4 versions stay in. Subtitles of the 3 foreign parts are real translations (SUBS); SUBS_HEAR = what is spoken.
P = [
 (8.38, 10.90, "hook"),  # auf vier oder fünf Sprachen jetzt erläutern
 (10.92, 11.86, "de1"),  # kommt in die
 (12.46, 13.38, "de2"),  # WhatsApp-Gruppe
 (13.78, 14.84, "de3"),  # um 15 Prozent
 (16.34, 18.64, "de4"),  # Discount zu bekommen, um Early Access zu bekommen,
 (19.90, 21.84, "de5"),  # um Pre-Sample-Review zu bekommen.
 (23.16, 25.00, "en0"),  # Und jetzt auf Englisch:
 (26.30, 28.92, "en1"),  # kommt in die WhatsApp-Gruppe,
 (29.44, 31.24, "en2"),  # um Discount zu bekommen,
 (33.32, 35.74, "en3"),  # um Sample Review zu bekommen und
 (36.48, 38.62, "en4"),  # Early Access zu bekommen. Und jetzt auf Französisch:
 (39.94, 42.90, "fr1"),  # Kommt in die Lavish WhatsApp-Gruppe,
 (43.32, 44.92, "fr2"),  # um Early Access zu bekommen,
 (46.84, 48.08, "fr3"),  # Discount zu bekommen
 (48.94, 52.10, "fr4"),  # und Sample Review. Und jetzt auf Spanisch!
 (52.42, 58.38, "es1"),  # Kommt in die Lavish WhatsApp-Gruppe, um Sample Review zu bekommen,
 (58.76, 60.12, "es2"),  # Discount zu bekommen
 (60.22, 62.18, "es3"),  # und Early Access zu bekommen.
 (64.04, 64.96, "adios"),# Adios!
]
SUBS = [  # shown on screen
 (8.40, 10.86, "AUF 4 ODER 5 *SPRACHEN* JETZT ERLÄUTERN"),
 (10.94, 13.36, "KOMMT IN DIE *WHATSAPP-GRUPPE*"),
 (13.80, 17.20, "UM *15 % DISCOUNT* ZU BEKOMMEN"),
 (17.22, 18.62, "UM *EARLY ACCESS* ZU BEKOMMEN"),
 (19.92, 21.82, "UM *PRE-SAMPLE-REVIEW* ZU BEKOMMEN"),
 (23.18, 24.98, "UND JETZT AUF *ENGLISCH*"),
 (26.32, 28.90, "COME INTO THE *WHATSAPP GROUP*"),
 (29.46, 31.22, "TO GET A *DISCOUNT*"),
 (33.34, 35.72, "TO GET A *SAMPLE REVIEW* AND"),
 (36.50, 37.60, "*EARLY ACCESS*"),
 (37.62, 38.60, "UND JETZT AUF *FRANZÖSISCH*"),
 (39.96, 42.88, "VENEZ DANS LE *GROUPE WHATSAPP* LAVISH"),
 (43.34, 44.90, "POUR AVOIR UN *EARLY ACCESS*"),
 (46.86, 48.06, "UNE *RÉDUCTION*"),
 (48.96, 50.80, "ET UNE *SAMPLE REVIEW*"),
 (50.82, 52.08, "UND JETZT AUF *SPANISCH*"),
 (52.44, 56.20, "VENID AL *GRUPO DE WHATSAPP* DE LAVISH"),
 (56.22, 58.36, "PARA RECIBIR UNA *SAMPLE REVIEW*"),
 (58.78, 60.10, "UN *DESCUENTO*"),
 (60.24, 62.16, "Y *EARLY ACCESS*"),
 (64.06, 64.94, "*ADIÓS*"),
]
SUBS_HEAR = [  # what is actually spoken (German) -> used by the speech checks
 (8.40, 10.86, "AUF VIER ODER FÜNF SPRACHEN JETZT ERLÄUTERN"),
 (10.94, 13.36, "KOMMT IN DIE WHATSAPP-GRUPPE"),
 (13.80, 17.20, "UM 15 PROZENT DISCOUNT ZU BEKOMMEN"),
 (17.22, 18.62, "UM EARLY ACCESS ZU BEKOMMEN"),
 (19.92, 21.82, "UM PRE-SAMPLE REVIEW ZU BEKOMMEN"),
 (23.18, 24.98, "UND JETZT AUF ENGLISCH"),
 (26.32, 28.90, "KOMMT IN DIE WHATSAPP-GRUPPE"),
 (29.46, 31.22, "UM DISCOUNT ZU BEKOMMEN"),
 (33.34, 35.72, "UM SAMPLE REVIEW ZU BEKOMMEN UND"),
 (36.50, 38.60, "EARLY ACCESS ZU BEKOMMEN UND JETZT AUF FRANZÖSISCH"),
 (39.96, 42.88, "KOMMT IN DIE LAVISH WHATSAPP-GRUPPE"),
 (43.34, 44.90, "UM EARLY ACCESS ZU BEKOMMEN"),
 (46.86, 48.06, "DISCOUNT ZU BEKOMMEN"),
 (48.96, 52.08, "UND SAMPLE REVIEW UND JETZT AUF SPANISCH"),
 (52.44, 58.36, "KOMMT IN DIE LAVISH WHATSAPP-GRUPPE UM SAMPLE REVIEW ZU BEKOMMEN"),
 (58.78, 60.10, "DISCOUNT ZU BEKOMMEN"),
 (60.24, 62.16, "UND EARLY ACCESS ZU BEKOMMEN"),
 (64.06, 64.94, "ADIOS"),
]
P = [(round(a*30)/30, round(b*30)/30, n) for a, b, n in P]
LOGO = 0.7
TONE = (68.0, 68.9)
NOISE = (68.0, 0.90)
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
