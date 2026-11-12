---
name: video-schnitt
description: Technischer Schnitt-Workflow mit ffmpeg für Lavish- und Owner-Videos – Analyse, 9:16-Format, Jump Cuts, Untertitel, Musik, Export. Verwenden, sobald ein Video tatsächlich bearbeitet, analysiert oder exportiert wird.
---

# Video-Schnitt – Technik & Workflow

## Standard-Exporteinstellungen
- Format: 1080x1920 (9:16), [AUSFÜLLEN falls abweichend]
- FPS: [AUSFÜLLEN – Standard 30]
- Codec: H.264 (`libx264`, `-crf 18`, `-preset slow`), Audio AAC 192k
- Lautheit: ca. -14 LUFS (`loudnorm=I=-14:TP=-1.5:LRA=11`)
- Dateiname: [AUSFÜLLEN – z. B. `JJJJ-MM-TT_typ_thema.mp4`]

## Schnittsprache (aus `LAVISH-GUIDELINES.md`)
**Bevorzugt:** harte Schnitte, bewusste Jump Cuts, rhythmische Schnitte, gelegentliche Freeze Frames,
unerwartete Bildausschnitte, Doku-Sequenzen, wechselndes Tempo (kurze schnelle Passagen, dann längere Einstellungen).
**Vermeiden:** generische CapCut-Übergänge, übermäßige Zooms, unnötige Motion Graphics, Glitch-Effekte,
Schnitt auf jeden einzelnen Beat, sich wiederholende Übergänge.
Der Schnitt soll spontan wirken, aber sorgfältig gebaut sein.

## Color Grading
- Leicht entsättigt, tiefe Schwarztöne mit erhaltener Zeichnung, natürliche Hauttöne
- Dezent kühle Untertöne, wo es passt; natürliches Licht und Umgebungsfarben erhalten
- Dezentes Filmkorn, wo es passt
- Pro Szene anpassen, nie ein Einheits-Filter über alles
- ffmpeg-Startpunkt (dezent, pro Clip prüfen): `eq=saturation=0.88:contrast=1.06,noise=alls=6:allf=t`

## Texturen (gezielt, nie das ganze Video überladen)
35mm-Korn, Blitzlicht-Fotos, Doku-Material, analoge Overlays, Fotokopie- und Magazin-Texturen.

## Sound
- Echte Umgebungsgeräusche erhalten (sie sind so wichtig wie Musik)
- Sound-Design nur dezent, für Atmosphäre
- **Keine** gehäuften Whooshes, künstlichen Impacts, generischen Werbe-Sounds (max. 2–3 pro Video, eher keine)

## Untertitel-Stil
- Font: **Bebas Neue** (`assets/fonts/BebasNeue-Regular.ttf`)
- Größe: klein, ASS-Fontsize 54 bei 1920 px Höhe (Großbuchstaben ca. 35 px hoch, wie im Original)
- Farbe: **Gelb #F0CC38**, **keine Kontur**, sondern **dunkler Schlagschatten nach rechts unten** (wie im Original)
- ASS-Style (PlayRes 1080x1920): `Style: Sub,Bebas Neue,54,&H0038CCF0,&H0038CCF0,&H00000000,&H59000000,0,0,0,0,100,100,0.5,0,1,0,3,8,170,170,0,1`, Position `{\an8\pos(540,1186)}`
- Satzzeichen weglassen (das Original hat keine)
- Hook-Überschrift: **#FCF0E4**, fette breite Schrift (NICHT Bebas Neue; laut Owner „Co Moderno“ aus CapCut, Datei fehlt noch), ca. 10 % der Bildhöhe pro Zeile, oberes Drittel, Pop-Animation, **hinter dem Owner** (Freistellung nötig)
- Position: [AUSFÜLLEN] – auf jeden Fall in der **TikTok-Safe-Zone**: oben
  ca. 15 % frei, unten ca. 25 % frei (Caption/Buttons), rechts ca. 15 % frei
  (Like-/Kommentar-Leiste). Das passt dann auch für die Instagram Story.
- Höhe im Owner-Content bisher: ca. 62–73 % von oben (liegt in der Safe-Zone)
- Wörter pro Einblendung: Owner-Content **4–8 Wörter / ganze Satzteile**
- Hervorhebung von Schlüsselwörtern: [AUSFÜLLEN – z. B. Akzentfarbe]
- Großbuchstaben: ja, immer (Bebas Neue)

## Workflow (immer so vorgehen)
1. **Analyse:** `ffprobe` für Länge/Auflösung/FPS. Alle ~1 Sek. einen Frame
   extrahieren (`ffmpeg -i in.mp4 -vf fps=1,scale=360:-1 frames/%03d.jpg`) und
   ansehen. Bei Sprache: Transkript mit Whisper erstellen (Wortzeitstempel).
2. **Typ klären:** Owner-Content oder Lavish-Content? → passenden Skill laden.
3. **Schnittplan** als kurze Liste (Zeitstempel + was passiert) erstellen und
   bei Unsicherheit dem Owner zeigen, bevor gerendert wird.
4. **Schneiden:** Stille entfernen (`silencedetect`), Clips mit `trim`/`concat`
   zusammensetzen, auf 9:16 croppen/skalieren.
5. **Untertitel:** `.ass`-Datei im Stil oben erzeugen und einbrennen.
6. **Audio:** Musik mischen (Stimme hat immer Vorrang, Musik ca. [AUSFÜLLEN] dB leiser), loudnorm.
7. **Kontrolle:** `performance-check` Skill durchgehen.
8. **Export** + kurze Vorschau-Frames dem Owner zeigen.
9. Feedback des Owners als Regel in den passenden Skill schreiben.

## Werkzeuge (getestet, Nov. 2026)
Die Cloud-Umgebung „Claude-get-know-me (Lavish Video)“ installiert beim Start
`faster-whisper`, `mediapipe` sowie `libegl1`/`libgles2`. Fehlt etwas, die Befehle von Hand ausführen.

**Transkript (Whisper):**
- Modell `small`, `device="cpu"`, `compute_type="int8"`, `language="de"`, `word_timestamps=True`
- `initial_prompt="Lavish, Pajel, Tom Bischof, Benno"`, damit Namen richtig geschrieben werden
- Bekannter Fehler: `av.open() ... metadata_errors`. Lösung: Audio vorher mit
  ffmpeg in Raw umwandeln (`-f f32le -ac 1 -ar 16000`) und als numpy-Array übergeben.
- Transkript danach **immer manuell prüfen** (z. B. „feier“ statt „fire“) und Namen korrigieren.

**Freistellung (Text hinter dem Owner):**
- MediaPipe `ImageSegmenter` mit Modell `selfie_multiclass_256x256.tflite`
  (storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/)
- Maske = 1 − Hintergrund-Konfidenz, leicht weichzeichnen (Blur ca. 1,5 px)
- Reihenfolge: Bild → Titeltext → Owner (Maske) darüber → Untertitel ganz oben
- Fürs Video pro Frame segmentieren (nur für die ca. 2,5 Sek. des Hook-Titels nötig)
- Eine `TypeError` beim Beenden von MediaPipe ist harmlos; die Ausgabe wird trotzdem gespeichert.

## Ordner
- Logo/Fonts: `assets/`
- Referenzen: `beispiele/`
- Fertige Videos nicht ins Git committen (zu groß) – nur auf Wunsch.

## Vorlage-Skripte (aus Test v1 „Neue Website“)
`tools/vorlage-owner-video/` enthält die getesteten Skripte (Pfade darin anpassen):
- `clean.py`: entfernt eingebrannte alte Untertitel/Überschrift per Inpainting (nur nötig, wenn das Material schon Text hat)
- `hook.py`: Hook-Überschrift mit Buchstaben-Pop **hinter dem Owner** (MediaPipe-Maske)
- `build.py`: Untertitel-Chunks (korrigierter Text), Jump Cuts (Pausen > 0,35 s raus), Zoom pro Chunk, ASS-Datei

Ablauf: Transkript → Text korrigieren → `build.py` → `ffmpeg -filter_complex_script graph.txt` → Untertitel einbrennen + `loudnorm` → Export.
Zoom-Anker: vertikal so, dass das Untertitelband an derselben Stelle bleibt (`y = 0.64·H·(1−1/z)`).

## Handgemachte Bausteine (Test v3, `tools/vorlage-owner-video/graphics_handmade.py`)
Alle prozedural erzeugt, jedes Mal leicht anders (Zufall), nie zweimal dieselbe Art hintereinander:
- **Klebeband-Label:** gelbes Gaffer-Tape, ausgefranste Enden, schwarze Bebas-Schrift mit Abrieb, 3–6° schief
- **Papierschnipsel:** abgerissenes Fotokopie-Papier, Schrift mit Kopier-Abrieb, weicher Schatten
- **Stempel-Wort:** riesig, abgenutzt, schief, **am Bildrand angeschnitten**, hinter dem Owner
- **Fotokopie-Standbild:** letzte 0,5 s eines Satzes einfrieren, Schwarz-Weiß mit Korn, gelbes Stempel-Wort darüber.
  Schatten vorher aufhellen (Gamma 0,62), damit Gesichter Zeichnung behalten.
- ~~Camcorder-/VHS-Rückblende~~ **gestrichen: Der Owner will den VHS-Look gar nicht** (auch keinen Datumsstempel). Nicht mehr verwenden.
- **Einblenden:** „hingeklatscht“ (2 Frames leicht versetzt, dann sitzt es), kein weiches Pop; Ausblenden per hartem Schnitt
- **Grading-Kette (ffmpeg):** `eq=saturation=0.86:contrast=1.07:brightness=-0.012,colorbalance=bs=0.035:bm=0.02:rs=-0.02`,
  dann Untertitel, zuletzt `noise=alls=9:allf=t` über alles (Korn verbindet Bild, Grafik und Text)
- **Kein** Whoosh, kein Sound-Effekt; Originalton bleibt
- `graphics_alt_v2_nicht_verwenden.py` ist der alte Baukasten-Look (Checkliste, Pop-Animationen) und nur als Negativbeispiel da.

## Aktuelle Pipeline (ab 12.11.2026): `tools/owner-video-v2/`
Ersetzt die Vorlage aus Test v1–v3 für neue Owner-Videos. Am Video „WhatsApp-Gruppe“ gebaut und komplett geprüft.
- `plan.py`: Schnittplan (Quellzeiten der Abschnitte), Untertitel-Texte, Zeit-Umrechnung. **Hier beginnt jedes neue Video.**
- `comp.py`: liest das Material **nach Frame-Nummern** (Bild und Ton bleiben exakt gleich lang), macht Kamera-Zoom
  (am Kopf verankert), Grading (nur aufs Material), Hook-Titel hinter dem Owner, alle Balken und Bewegungen, Schlussbild.
- `qa.py`: die Pflicht-Selbstkontrolle als Skript. **Muss „ALLES BESTANDEN“ melden, bevor der Owner etwas bekommt.**

**Ablauf:**
1. Mehrere Clips zuerst zu einem Master zusammenfügen (30 fps). Sätze laufen oft über Clip-Grenzen.
2. Sprach-Abschnitte per Lautstärke messen (Bandpass 250–3200 Hz, 10-ms-Hüllkurve). **Whisper-Zeitmarken sind bei Pausen
   bis zu 0,4 s daneben**; Schnitt- und Grafikzeiten deshalb an den gemessenen Abschnitten ausrichten.
3. Text mit `large-v3` und **ganzen Sätzen als Kontext** transkribieren. Kurze Schnipsel und Vorgabe-Wörter (initial_prompt)
   führen zu falschen Wörtern. Unklare Wörter mit mehreren Modellen gegenprüfen, sonst den Owner fragen.
4. Kopfposition pro Abschnitt messen (MediaPipe), danach Zoom/Bildausschnitt und Platz für Grafiken festlegen.
5. Ton: `highpass=75, afftdn=nr=9`, dann feste Verstärkung auf -14 LUFS + Limiter (kein dynamisches loudnorm).
6. Export: `-crf 19 -maxrate 12M -bufsize 24M`. **Ohne Obergrenze bläht das Korn die Datei auf über 300 MB auf.**

**Gestaltung (erwachsener Look):**
- Balken: Bebas Neue, gerade Kanten, weicher Schatten. Stile: Gelb/Schwarz, Schwarz/Beige, Beige/Schwarz.
  Hierarchie: **ein großer Balken (Größe 96) + kleinere Zeilen (Größe 70)**, linksbündig an x=64, ab y=300.
- Owner per Zoom 1,18 nach rechts rücken (Kopf bei x≈650), dann ist links Platz. Zeilen neben dem Kopf max. ca. 480 px breit.
- Bewegung: Einflug 0,28 s mit Überschwingen + Bewegungsunschärfe, langsame Drift beim Halten, Rausfahren 0,17 s,
  Text-Roll im selben Balken (Morph), Hochzählen, einmaliger Licht-Sweep, Kamera-Push bei Pointen.
- Balken dürfen über Jump Cuts hinweg stehen bleiben (verbindet die Schnitte).
- Hook-Titel beige hinter dem Owner, bei heller Wand mit weichem dunklem Schatten; Material oben leicht abdunkeln.
- QR-Code: mind. 4 s sichtbar, mind. 360 px, Lesbarkeit aus dem fertigen Video prüfen (auch verkleinert).
- Schlussbild: schwarzer Grund, Logo groß, darunter optional Balken + QR. 2,2 s.

## Gelernte Regeln (wird laufend durch Feedback ergänzt)
- **Feedback zum Video „WhatsApp-Gruppe“ v1 (Owner: „fast perfekt“), umgesetzt in v2:**
  - **Screenshots des Owners per Motion einbauen**, als gerahmte Karte ohne Handy-Rahmen (8 px schwarzer Rand, weicher Schatten),
    ca. 300 px breit links neben dem Owner. Wichtige Stelle mit **gelbem Rahmen markieren**; kleiner Text (z. B. ein Banner)
    **springt groß aus der Karte heraus** (hier 700 px breit). Pop-up „poppt“ mit Überschwingen ins Bild.
    Zuschnitte liegen in `assets/website/` (Startseite, Pop-up, Banner von lavishclo.com).
  - **Pausen mit neuem Ansatz mitten im Satz herausschneiden** („…Drop habe | werde ich da Verlosungen“). Der Owner hört
    solche Stolperer sofort. Jede Pause über ca. 0,5 s im Satz prüfen und im Zweifel schließen.
  - **Nach einer Aussage nicht zu schnell in die nächste Szene schneiden**: mind. 0,4 s Luft nach dem letzten Wort,
    wenn danach Thema oder Bildausschnitt wechselt. Kein harter Punch-in direkt danach.
  - Technik: Ein gespeichertes Grafik-Bild nie direkt verändern (immer `.copy()`), sonst wird es beim Einblenden dauerhaft blass.
- **12.11.2026, aus der Selbstkontrolle gelernt:**
  - Nie in einer Sprechpause **innerhalb eines Wortes** schneiden („Grup-pe“ wurde abgeschnitten). Vor dem Schnitt prüfen,
    ob in den nächsten 0,5 s noch ein kurzer Laut folgt. Im Zweifel den Satz ungeschnitten lassen.
  - Jeden weggeschnittenen Sprach-Abschnitt begründen (qa.py Punkt 3).
  - Beim Prüfen Stereo nie einfach zu Mono zusammenlegen (täuscht Clipping vor).
  - Untertitel-Größe bleibt 54 (nicht eigenmächtig ändern).
- **12.11.2026:** v3-Bausteine wirken zu kindlich. Papierschnipsel, Fransen-Tape und starke Schräglagen nicht mehr verwenden.
  Balken sauber und gerade, Akzente nur Gelb/Weiß/Schwarz. Motion nach `owner-content` („Update 12.11.“):
  Einflug mit Motion Blur, Überschwingen, Drift beim Halten, Hochzählen, Licht-Sweep, Morph.
- **12.11.2026:** Vor jedem Senden die Pflicht-Selbstkontrolle aus `performance-check` vollständig durchgehen.
- **Feedback zu Test v3 (Owner):**
  - **VHS-/Camcorder-Effekt komplett weglassen.** Gilt für alle Videos.
  - **Klebeband-Balken und Papierschnipsel mit der „hingeklatscht“-Bewegung: gefallen, beibehalten.**
  - **Riesiges Stempel-Wort hinter dem Kopf (wie „FIRE“): beibehalten.**
- Zoom-Stufen: normal 1.0, Punch-in 1.12–1.18, starke Aussage 1.22–1.25.
  **Laut Guidelines sparsam:** nur bei echten Kernaussagen (Richtwert 4–6 Wechsel pro 40 s, nicht bei jedem Satz).
  Test v1/v2 hatten 22 Wechsel. **Festgelegt:** ruhiger Schnitt wie in Referenz 3, Zooms nur bei Kernaussagen (ca. 4–8 pro Video); das Tempo kommt von den Einblendungen (siehe `owner-content`, „Grafik-Sprache“).
- Hook-Überschrift: bis die Fontdatei von „Co Moderno“ vorliegt, Platzhalter **Rubik Black, horizontal auf 80 % gestaucht**.
- Videos immer prüfen: Schnittstellen anhören (keine abgeschnittenen Wörter), Frames bei jedem Zoom ansehen.
