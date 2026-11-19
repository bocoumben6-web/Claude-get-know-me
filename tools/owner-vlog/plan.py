"""Vlog 1 (Content-Tag / Rosa Tunnel, 18.11.2026) – Schnittplan.
Jedes Segment: (clip, in, out, ton). ton: 'voice' = Stimme bleibt (entrauscht), 'music' = stumm (Owner legt Musik drunter).
'SWITCH' = GTA-Switch vom letzten Bild davor zum ersten Bild danach.
Untertitel: Gruppen von Wörtern mit Quell-Zeit (Sekunden im Clip), Wort für Wort aufbauend."""
import os
JOB = os.environ.get("JOB", "/tmp/claude-0/-home-user-Claude-get-know-me/019e819c-46ae-555e-8d8d-6adb89d74114/scratchpad/raw")
CLIPS = JOB + "/clips"

SEGMENTS = [
    ("4653", 0.00, 4.35, "voice"),     # Ich hab lange keinen Vlog mehr gehabt. Heute ist Content-Tag.
    ("4653", 6.55, 14.75, "voice"),    # Ja ich will ... Black Friday ... Beanies ... der Luis
    ("4653", 15.12, 16.55, "voice"),   # und los geht's
    ("4654", 0.00, 3.36, "music"),     # Kumpel läuft auf die Kamera zu
    "SWITCH",
    ("4655", 0.00, 0.73, "music"),     # Hand im Auto
    ("4656", 0.00, 2.03, "music"),     # Fahrt
    ("4657", 0.00, 1.66, "music"),     # Ankunft
    ("4658", 0.00, 2.13, "music"),     # Begrüßung an der Station
    ("4659", 0.00, 6.05, "voice"),     # Location switchen, zu windig
    ("4659", 7.25, 9.62, "voice"),     # wir müssen in einen Tunnel gehen
    ("4659", 10.72, 13.95, "voice"),   # ja aber wird schon
    "SWITCH",
    ("4660", 0.00, 3.20, "voice"),     # Das ist die neue Location, der Rosa Tunnel
    ("4661", 0.00, 1.63, "music"),
    ("4662", 0.00, 1.93, "music"),
    ("4665", 0.00, 2.46, "voice"),     # Warte, warte, warte
    ("4668", 0.00, 2.50, "voice"),     # Ich verstehe diese Menschen nicht
    ("4704", 0.00, 5.55, "voice"),     # "Ich bin jetzt fertig mit dem Video, danke ..." (Ende: Kamera kippt -> weg)
    ("4705", 0.00, 2.79, "music"),     # Rückfahrt
    "SWITCH",
    ("4706", 0.00, 3.60, "music"),     # Essen, Kumpel mit Flasche
    ("4708", 2.20, 4.20, "music"),     # am Tisch
    ("4708", 5.60, 7.60, "music"),     # Pommes füttern
    ("4710", 0.00, 3.00, "music"),     # Nachtfahrt
    "SWITCH",
    ("4711", 1.20, 4.70, "voice"),     # "Zu windig, Wallah, aber jetzt erstmal Motorworld, Autos gucken" (quer gedreht)
    ("4712", 0.00, 2.10, "voice"),     # Autohalle: "Gucken wir mal kurz, ein Schnäppchen"
    ("4712", 2.80, 9.25, "voice"),     # "entweder wird es der oder der ... ich weiß es doch nicht, Bro"
    ("4714", 0.25, 2.45, "voice"),     # Parkhaus: "Ab nach Hause, es werden noch Videos geschnitten"
    ("4714", 3.12, 4.80, "voice"),     # "Ja, das war der Tag für heute."  (quer gedreht) -> Schluss
]
SWITCH_LEN = 0.4          # Whip-Pan, Sekunden (12 Frames)
ROTATE = {"4662": "transpose=2", "4711": "transpose=2", "4714": "transpose=2"}     # Metadaten falsch: Inhalt liegt quer
PORTRAIT = set()                     # Owner 19.11.: Hochkant-Clips raus
NOISE = {"4711": (4.7, 5.05), "4714": (0.0, 0.55), "4704": (5.6, 6.5), "4712": (11.2, 13.6), "4653": (4.6, 6.4), "4659": (6.1, 7.2), "4660": (2.4, 3.2), "4665": (0.0, 0.3), "4668": (0.0, 1.1)}

# (clip, [(wort, start_im_clip), ...], ende_im_clip)
SUBS = [
    ("4653", [("ICH", .25), ("HAB", .42), ("LANGE", .48)], .58),
    ("4653", [("KEINEN", .58), ("VLOG", .72), ("MEHR", .80), ("GEHABT", .92)], 1.9),
    ("4653", [("HEUTE", 2.66), ("IST", 3.06), ("CONTENT-TAG", 3.26)], 4.3),
    ("4653", [("JA", 6.62), ("ICH", 6.95), ("WILL", 7.32)], 7.68),
    ("4653", [("EIN", 7.68), ("KLEINES", 7.84), ("DING", 8.06), ("DREHEN", 8.60)], 9.02),
    ("4653", [("WEIL", 9.02), ("FÜR", 9.72), ("BLACK", 10.16), ("FRIDAY", 10.40)], 10.76),
    ("4653", [("BRING", 10.76), ("ICH", 11.28), ("BEANIES", 11.42), ("RAUS", 11.72)], 12.2),
    ("4653", [("UND", 12.30), ("JA", 12.78), ("DAS", 13.12), ("IST", 13.38)], 13.64),
    ("4653", [("SCHON", 13.52), ("DER", 13.64), ("LUIS", 13.76)], 14.7),
    ("4653", [("UND", 15.15), ("LOS", 15.30), ("GEHT'S", 16.0)], 16.5),
    ("4659", [("WIR", .0), ("MÜSSEN", .05), ("JETZT", .16)], .42),
    ("4659", [("DIE", .32), ("LOCATION", .42), ("SWITCHEN", .96)], 1.70),
    ("4659", [("WEIL", 1.70), ("ES", 2.44), ("ZU", 2.56), ("WINDIG", 2.70), ("IST", 3.12)], 3.36),
    ("4659", [("UND", 3.36), ("WIR", 3.70), ("ANGST", 3.92), ("HABEN", 4.14)], 4.52),
    ("4659", [("DASS", 4.52), ("MAN", 4.68), ("UNS", 4.92), ("DANN", 5.20)], 5.34),
    ("4659", [("NICHT", 5.34), ("GESCHEIT", 5.48), ("HÖRT", 5.80)], 6.05),
    ("4659", [("WIR", 7.40), ("MÜSSEN", 7.84), ("IN", 8.20)], 8.92),
    ("4659", [("EINEN", 8.92), ("TUNNEL", 9.06), ("GEHEN", 9.32)], 9.62),
    ("4659", [("JA", 10.75), ("ABER", 10.94)], 12.26),
    ("4659", [("WIRD", 12.26), ("SCHON", 13.36)], 13.95),
    ("4660", [("DAS", 0.0), ("IST", 0.0), ("DIE", 0.04), ("NEUE", 0.12), ("LOCATION", 0.24)], 0.88),
    ("4660", [("DER", 0.88), ("ROSA", 1.30), ("TUNNEL", 1.64)], 2.6),
    ("4665", [("WARTE", 0.32), ("WARTE", 0.96), ("WARTE", 1.34)], 2.2),
    ("4668", [("ICH", 1.20), ("VERSTEHE", 1.54), ("DIESE", 1.84), ("MENSCHEN", 1.92), ("NICHT", 2.06)], 2.5),
    ("4704", [("ICH", 0.0), ("BIN", 0.02), ("JETZT", 0.08), ("FERTIG", 0.20)], 0.24),
    ("4704", [("MIT", 0.24), ("DEM", 0.36), ("VIDEO", 0.48)], 0.72),
    ("4704", [("DANKE", 0.72)], 1.30),                       # Name danach unsicher -> Owner fragen
    ("4704", [("DANKE", 1.30), ("ANDI", 1.46)], 1.74),
    ("4704", [("DANKE", 1.74), ("LUIS", 1.82)], 2.24),
    ("4704", [("DANKE", 2.24), ("MUSTAFA", 2.48)], 2.86),
    ("4704", [("HINTER", 2.86), ("DER", 3.18), ("KAMERA", 3.30)], 3.64),
    ("4704", [("WIR", 3.64), ("GEHEN", 3.70), ("JETZT", 3.94), ("NATÜRLICH", 4.18)], 4.9),
    ("4712", [("GUCKEN", 0.0), ("WIR", 0.08), ("MAL", 0.20), ("BRUDER", 0.30)], 0.58),
    ("4712", [("SCHNÄPPCHEN", 0.58), ("WEISST", 1.14), ("DU", 1.38)], 2.06),
    ("4712", [("ENTWEDER", 2.82), ("WIRD", 3.14), ("ES", 3.30), ("DER", 3.44), ("BRUDER", 3.54)], 3.88),
    ("4712", [("ODER", 3.88), ("DER", 3.96), ("BRUDER", 4.12)], 4.54),
    ("4712", [("ABER", 4.54), ("ES", 4.62), ("KANN", 4.74), ("AUCH", 4.82), ("SEIN", 4.90)], 5.02),
    ("4712", [("ES", 5.02), ("WIRD", 5.12), ("DER", 5.16), ("DA", 5.34), ("HINTEN", 5.44), ("BRUDER", 5.72)], 5.92),
    ("4712", [("ABER", 5.92), ("ES", 6.02), ("KANN", 6.16), ("AUCH", 6.36), ("SEIN", 6.54), ("BRUDER", 6.80)], 6.96),
    ("4712", [("ES", 6.96), ("WIRD", 7.08), ("DER", 7.20)], 7.58),
    ("4712", [("OH", 7.58), ("ICH", 7.88), ("WEISS", 8.02), ("ES", 8.30), ("DOCH", 8.48), ("NICHT", 8.64), ("BRO", 8.96)], 9.25),
    ("4711", [("ZU", 1.30), ("WINDIG", 1.34)], 1.82),
    ("4711", [("WALLAH", 1.82)], 2.12),
    ("4711", [("ABER", 2.12), ("JETZT", 2.32), ("ERSTMAL", 2.58), ("MOTORWORLD", 2.90)], 3.60),
    ("4711", [("AUTOS", 3.64), ("GUCKEN", 4.36)], 4.70),
    ("4714", [("AB", 0.36), ("NACH", 0.66), ("HAUSE", 0.80)], 1.16),
    ("4714", [("ES", 1.16), ("WERDEN", 1.26), ("NOCH", 1.42)], 1.58),
    ("4714", [("VIDEOS", 1.58), ("GESCHNITTEN", 1.78)], 2.45),
    ("4714", [("JA", 3.22)], 3.66),
    ("4714", [("DAS", 3.66), ("WAR", 3.78), ("DER", 3.92), ("TAG", 4.00)], 4.18),
    ("4714", [("FÜR", 4.18), ("HEUTE", 4.26)], 4.80),
]
