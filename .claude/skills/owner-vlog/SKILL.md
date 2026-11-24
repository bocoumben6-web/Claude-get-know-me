---
name: owner-vlog
description: Stil für den zweiten Account des Owners (Owner-Vlogs, Tagesvlog durch die Stadt) – Selfie-Vlog im Gehen, Street-B-Roll mit Musik, Leute treffen, gelbe Wort-für-Wort-Untertitel, GTA-Switch bei Ortswechsel. Verwenden, wenn ein Vlog für den neuen Owner-Account geschnitten wird. Nicht für Lavish-Talking-Head-Videos (dafür owner-content / lavish-setup).
---

# Owner-Vlog (zweiter Account, ab 18.11.2026)

**Eigenes Format, nicht mit Lavish mischen.** Das Lavish Setup (Balken, Hook hinter dem Owner,
Lavish-Logo am Ende) gilt hier **nicht automatisch**. Technik aus `video-schnitt` gilt weiter
(HDR umrechnen, Dubletten prüfen, nie im Wort schneiden, Stimm-Kette aus `lavish-setup`, Export ohne Korn).
Selbstkontrolle vor dem Senden bleibt Pflicht.

## Referenz 1 (vom Owner, 18.11.2026, TikTok, 69 s, München-Tag)
Analysiert aus dem TikTok-Download (1024×576, 16:9 quer, 30 fps).

**Aufbau**
- 0–8 s: Selfie im Gehen (Treppenhaus/Hauseingang), direkt reden, Pfandflaschen abgeben → witziger, echter Einstieg
- 8–23 s: **Stadt-B-Roll ohne Reden** (Ludwigstraße, Café-Terrassen, Odeonsplatz, Radfahrer, BUS-Spur),
  Schnitt alle ca. 1,5–4 s, hier läuft Musik → **das sind die Stellen, wo der Owner Musik drunterlegt**
- 23–40 s: Café: Leute bestellen, Freunde am Tisch, jeder bekommt **seinen Namen als Untertitel** (KARINA, MURAT, ANGELO)
- 40–56 s: Straße, Leute treffen, Outfits zeigen („ZEIG ZEIG“), Close-ups auf Schuhe/Jorts, Lavish getragen („T LAVISH“)
- 56–60 s: Sonnenuntergang, Freund versteckt sich hinter Laterne → kleine Pointe
- 60–69 s: Abschluss als Selfie (Hoodie, anderer Tag/Ort): Ausblick, „gebt euer Bestes, Leute“. Kein Logo, kein CTA.

**Schnitt**
- Nur **harte Schnitte**, ca. 22 Schnitte in 69 s (Ø alle 3 s). Keine Zooms, keine Grafiken, keine Balken.
- Selfie-Teile laufen länger, B-Roll ist schnell geschnitten.
- Kein Grading-Look: natürliche, sonnige iPhone-Farben.

**Untertitel**
- **Bebas Neue, Gelb (wie #F0CC38)**, ohne sichtbare Kontur, ganz leichter Schatten
- **Wort für Wort aufbauend:** „SPANNEND“ → „SPANNEND OKAY“ → „SPANNEND OKAY FALSCHE“, dann neue Zeile von vorn
  (je ca. 1–4 Wörter, eine Zeile)
- Position: **genau mittig** (horizontal und vertikal, ca. 48–50 % von oben), Größe ca. 6 % der Bildhöhe
- Laufen überall, wo gesprochen wird, auch bei Leuten im Hintergrund; Namen der Leute groß als Untertitel

**Ton**
- Musik läuft unter dem ganzen Video, Stimme darüber. In B-Roll-Strecken nur Musik.
- Für unseren Export: Musik-Stellen **stumm** lassen (Owner legt Musik in der App drauf) + Zeitliste mitschicken.

## Übergang bei Ortswechsel (Stand 19.11.2026)
**Owner-Entscheidung beim ersten Vlog: GTA-Switch raus, stattdessen eine „coole Transition“.** Umgesetzt als
**Whip-Pan** (`whip_frames`): 12 Frames (0,4 s), altes Bild reißt nach links weg, neues zieht von rechts rein,
horizontale Bewegungsunschärfe folgt dem Tempo (Mitte am schnellsten), ein Whoosh in der Mitte.
Ob der GTA-Switch später zurückkommt: offen. Der Owner wollte einen echten GTA-Clip als Vorlage schicken; dann danach bauen.

### Alter Versuch: GTA-Switch (18.11.2026, „wie beim Charakterwechsel in GTA 5“), aktuell nicht verwenden
- Bei **jedem Ortswechsel**. In Referenz 1 nicht zu sehen (dort nur harte Schnitte).
- Umsetzung (`tools/owner-vlog/build.py`, `switch_frames`), 1,0 s bei 30 fps:
  1. **3 Sprünge nach oben** (je 4 Frames, schnell anfahren, weich abbremsen): Kamera fährt aus dem letzten Bild
     hoch in einen Himmel, vertikale Bewegungsunschärfe, bei jedem Sprung ein kurzer heller Ruck
  2. Mit jedem Sprung **entsättigter, kühler, flacher** (GTA-Look), oben fast grau
  3. **Schwenk** über den Himmel (6 Frames, horizontale Unschärfe)
  4. **3 Sprünge runter** ins erste Bild des neuen Orts, Farbe kommt zurück
  5. Ton: pro Sprung ein dumpfer Schlag, Luftzug beim Schwenk (selbst erzeugt, keine Spiel-Sounds)
- **Nicht** mit gespiegelter/verkleinerter Umgebung arbeiten: sieht aus wie ein Kaleidoskop (getestet, verworfen).
- Himmel wird selbst erzeugt (blass, Wolken). Keine Grafiken, Sounds oder Karten aus dem Spiel verwenden.

## Festgelegt (Owner, 18.11.2026)
- **Format quer 16:9** (1920×1080), wie der alte Vlog. **Hochkant-Clips kommen raus** (Owner, 19.11.2026), nicht auf unscharfen Hintergrund setzen.
  Clips mit falscher Drehung (Metadaten) im Bild prüfen: Ist der Inhalt eigentlich quer, richtig drehen und behalten.
- **Kein Logo am Ende**, harter Schluss wie im alten Vlog.
- Stumme Stellen (B-Roll ohne Reden) bekommen Musik vom Owner; Zeitliste mitschicken.
- Untertitel nur, wo die Spracherkennung sicher ist (mit zweitem Durchlauf prüfen); unsichere Stellen dem Owner nennen.

## Werkzeug (Stand Vlog 2, 24.11.2026)
- `tools/owner-vlog/build.py` mit `PLAN=plan_<name> JOB=<ordner> python3 build.py`. Plan pro Vlog als eigene Datei.
- `SUBS = None` -> Untertitel automatisch aus der fertig geschnittenen Stimme (Wortzeiten passen exakt).
  Danach den Wortlaut **immer selbst lesen** und Fehler über `REPLACE`/`FIX` im Plan korrigieren
  (Beispiele: „die haben gekackt“ statt „gar keinen Bock“, „Levelstand/Levish“ statt „Lavish“).
- Clips mit Musik im Original (Tanz/Flex) als stumme B-Roll behandeln, nicht untertiteln.
- Immer zusätzlich eine **Handy-Fassung** (~6 Mbit/s, unter 100 MB) schicken: große Dateien lassen sich in der App nicht laden.

## Namen & Orte (vom Owner bestätigt)
- Freunde: **Harouna**, Andi, Luis, Mustafa (filmt oft). Spracherkennung macht aus Harouna „Ronald/Haruna“.
- **Motorworld** (München, Autohalle). Spracherkennung hört „Motorhaut/Motoruhr“.

## Gelernte Regeln (wird laufend durch Feedback ergänzt)
- Hochkant-Clips nicht verwenden (19.11.2026). **Ausnahme (Owner):** Ist ein „Hochkant“-Clip eigentlich quer gefilmt und nur seitlich
  gespeichert (Köpfe liegen im Bild auf der Seite), wird er quer gedreht und verwendet. Jeden Hochkant-Clip daraufhin ansehen.
- **Untertitel unten und kleiner** (Owner, 19.11.2026): Bebas Neue Gelb, Größe 62 bei 1080p, Mitte bei 86 % der Bildhöhe
  (statt groß in der Bildmitte wie in Referenz 1).
- Doppelt hochgeladene Dateien („IMG_xxxx (1).MOV“) prüfen: unterscheiden sich oft nur im Datei-Kopf -> nur einmal verwenden.
- **Stumme B-Roll-Clips kurz halten** (Owner, 19.11.2026): je ca. 1,2–2 s, nur der beste Moment (Umarmung, Pommes füttern …).
  Clips, in denen geredet wird, behalten ihre Länge.
- Clip-Enden prüfen: Kippt/schwenkt die Kamera am Ende weg, vorher schneiden (an einer Wortgrenze).
- Kein GTA-Switch, solange der Owner ihn nicht wieder freigibt; Whip-Pan als Übergang (19.11.2026).
