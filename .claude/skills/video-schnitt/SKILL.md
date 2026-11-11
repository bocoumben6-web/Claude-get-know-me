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
- Font: siehe `lavish-brand`
- Größe: [AUSFÜLLEN]
- Farbe / Rand / Schatten: [AUSFÜLLEN]
- Position: [AUSFÜLLEN – z. B. mittleres Drittel, nicht ganz unten wegen App-UI]
- Wörter pro Einblendung: [AUSFÜLLEN – z. B. 1–3]
- Hervorhebung von Schlüsselwörtern: [AUSFÜLLEN – z. B. Akzentfarbe]
- Großbuchstaben: [AUSFÜLLEN]

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

## Ordner
- Logo/Fonts: `assets/`
- Referenzen: `beispiele/`
- Fertige Videos nicht ins Git committen (zu groß) – nur auf Wunsch.

## Gelernte Regeln (wird laufend durch Feedback ergänzt)
- (noch leer)
