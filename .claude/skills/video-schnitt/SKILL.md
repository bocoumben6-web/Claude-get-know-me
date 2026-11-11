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
35mm-Korn, VHS/MiniDV-Look, Blitzlicht-Fotos, Doku-Material, analoge Overlays, Fotokopie- und Magazin-Texturen.

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

## Gelernte Regeln (wird laufend durch Feedback ergänzt)
- Zoom-Stufen: normal 1.0, Punch-in 1.12–1.18, starke Aussage 1.22–1.25.
  **Laut Guidelines sparsam:** nur bei echten Kernaussagen (Richtwert 4–6 Wechsel pro 40 s, nicht bei jedem Satz).
  Test v1/v2 hatten 22 Wechsel. **Menge noch offen**, wird am Referenzvideo des Owners festgelegt (siehe Hinweis in `LAVISH-GUIDELINES.md`).
- Hook-Überschrift: bis die Fontdatei von „Co Moderno“ vorliegt, Platzhalter **Rubik Black, horizontal auf 80 % gestaucht**.
- Videos immer prüfen: Schnittstellen anhören (keine abgeschnittenen Wörter), Frames bei jedem Zoom ansehen.
