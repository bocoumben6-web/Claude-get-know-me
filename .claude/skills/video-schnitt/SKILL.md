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

## Untertitel-Stil
- Font: **Bebas Neue** (`assets/fonts/BebasNeue-Regular.ttf`)
- Größe: klein, ca. 2,4 % der Bildhöhe (bei 1920 px Höhe ca. 46 px)
- Farbe: **Gelb #F0CC38**, dünne dunkle Kontur (2–3 px) oder leichter Schatten
- Hook-Überschrift: **#FCF0E4**, fette breite Schrift (NICHT Bebas Neue, Name noch offen), ca. 10 % der Bildhöhe pro Zeile, oberes Drittel, Pop-Animation, **hinter dem Owner** (Freistellung nötig)
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

## Gelernte Regeln (wird laufend durch Feedback ergänzt)
- (noch leer)
