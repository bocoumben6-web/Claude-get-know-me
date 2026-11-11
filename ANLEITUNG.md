# Anleitung: So bringst du Claude deinen Videostil bei

Diese Anleitung erklärt, **welche Skills Claude braucht**, um deine Videos für
**Lavish** (Brand-Content) und für **dich als Owner** (Personal Branding) so zu
schneiden, wie du sie willst – und **wie du Claude diese Skills beibringst**.

---

## 0. Ehrlich vorweg: Was Claude kann und was nicht

| Kann Claude | Kann Claude nicht (oder nur eingeschränkt) |
|---|---|
| Videos per **ffmpeg** schneiden, kürzen, zusammensetzen | Kein Premiere/CapCut/Final Cut mit Maus bedienen (außer über Computer-Use auf deinem Rechner) |
| Auf **9:16 (Reels/TikTok/Shorts)** zuschneiden, skalieren, croppen | Videos nicht „anschauen“ wie ein Mensch – Claude sieht **Standbilder (Frames)** und liest das **Transkript** |
| **Untertitel** einbrennen (Schrift, Farbe, Position nach deinem Stil) | Keine Garantie, dass ein Video viral geht – nur bessere Chancen |
| Stille / „ähm“-Pausen rausschneiden (Jump Cuts) | Lizenzierte Musik besorgen – Musik musst du liefern oder in der App hinzufügen |
| Musik unterlegen, Lautstärke anpassen, Ton normalisieren | Trends live auf TikTok/Instagram mitverfolgen (nur, wenn du sie zeigst/beschreibst) |
| Hooks, Captions, Hashtags und Skripte schreiben | |
| Aus deinen Zahlen (Views, Watchtime) lernen, was funktioniert | |

**Wichtig:** Claude „lernt“ nicht automatisch dazu. Alles, was Claude über
deinen Stil wissen soll, muss **in den Skill-Dateien in diesem Repository
stehen**. Jede neue Session liest diese Dateien – das ist Claudes Gedächtnis.

---

## 1. Welche Skills Claude wirklich braucht

In diesem Repository liegen dafür schon 5 vorbereitete Skills unter
`.claude/skills/`. Du musst sie nur noch **mit deinem Wissen füllen**
(überall, wo `[AUSFÜLLEN]` steht).

| # | Skill | Wofür | Wichtigkeit |
|---|---|---|---|
| 1 | `lavish-brand` | Wer ist Lavish? Schriftweise, Farben, Fonts, Logo, Ton, Zielgruppe, No-Gos | ⭐⭐⭐ Pflicht |
| 2 | `owner-content` | Dein Personal-Branding-Stil: Talking-Head, Storytelling, wie du redest, Hooks | ⭐⭐⭐ Pflicht |
| 3 | `lavish-product-content` | Pieces-Videos ohne/mit wenig Reden: Schnitt auf Beat, Close-ups, Atmosphäre | ⭐⭐⭐ Pflicht |
| 4 | `video-schnitt` | Die Technik: Format, Untertitel-Look, Schnitttempo, Musiklautstärke, Export | ⭐⭐⭐ Pflicht |
| 5 | `performance-check` | Checkliste vor dem Export + Lernen aus deinen Statistiken | ⭐⭐ Sehr wichtig |

Warum getrennt? Weil Owner-Content und Lavish-Content **komplett anders**
funktionieren. Claude soll nie den Stil vermischen.

---

## 2. So bringst du Claude die Skills bei – Schritt für Schritt

### Schritt 1: Brand-Grundlagen ausfüllen (ca. 30 Min.)
Öffne `.claude/skills/lavish-brand/SKILL.md` und fülle alles aus.
Wenn dir Schreiben zu viel ist: **Sprich es Claude einfach ein** (Sprachnachricht
ist okay) und sag: *„Trag das in den lavish-brand Skill ein.“*

Liefere am besten auch:
- Logo als PNG mit transparentem Hintergrund → `assets/logo.png`
- Deine Schriftarten (.ttf/.otf) → `assets/fonts/`
- Farbcodes (z. B. `#000000`, `#C9A96E`)

### Schritt 2: Referenzvideos sammeln (das Wichtigste!)
Claude lernt am besten durch **Beispiele**. Sammle:

| Ordner | Was rein soll | Wie viele |
|---|---|---|
| `beispiele/gute-videos/` | Deine Videos, die **am besten performt** haben | 5–10 |
| `beispiele/schlechte-videos/` | Videos, die **schlecht liefen** | 3–5 |
| `beispiele/rohmaterial/` | Ungeschnittenes Material + das fertige Video dazu | 2–3 Paare |

Zu **jedem** Video eine kurze Notiz in `beispiele/NOTIZEN.md`:
- Views / Likes / Saves / Shares / durchschnittliche Wiedergabedauer
- Warum hat es (nicht) funktioniert? Deine Meinung reicht.
- Owner-Content oder Lavish-Content?

> Große Videodateien gehören eigentlich nicht in Git. Für Referenzen reichen
> **kurze, komprimierte Versionen** (Claude kann sie dir verkleinern) oder du
> lädst sie direkt in der Session hoch. Es geht um Stil, nicht um 4K-Qualität.

Dann sag zu Claude:
> *„Analysiere die Videos in `beispiele/` und schreib die Muster, die du findest,
> in die passenden Skills.“*

Claude zieht dann Frames und Transkripte raus, misst Schnitttempo, Länge,
Untertitel-Stil, Hook-Länge usw. und trägt es ein. **Du prüfst und korrigierst.**

### Schritt 3: Inspiration von anderen Accounts
Screenshots oder kurze Clips von Accounts/Videos, deren **Stil** du magst, mit
einem Satz, was genau dir gefällt („die Untertitel“, „der Übergang bei 0:03“).
Claude soll den Stil verstehen, **nicht kopieren**.

### Schritt 4: Erste Test-Edits (Feedback-Schleife)
1. Gib Claude Rohmaterial + sag, ob Owner- oder Lavish-Content.
2. Claude schneidet eine Version.
3. Du gibst **konkretes** Feedback:
   - ❌ „Gefällt mir nicht“
   - ✅ „Hook zu langsam, die ersten 2 Sekunden raus“
   - ✅ „Untertitel kleiner, weiter oben, nur 2–3 Wörter gleichzeitig“
4. **Ganz wichtig:** Sag danach immer:
   > *„Speicher das als Regel im Skill.“*

   Nur so merkt sich Claude das für die nächsten Videos.
5. Wenn es passt: *„Commit und push.“* → dann ist es dauerhaft gespeichert.

Nach ca. **5–10 Videos** mit Feedback sollte Claude deinen Stil gut treffen.

### Schritt 5: Performance zurückmelden (laufend)
Wenn ein Video online ist, nach 2–7 Tagen die Zahlen an Claude geben
(Screenshot der Insights reicht). Sag:
> *„Trag das in den performance-check Skill ein und sag mir, was wir
> nächstes Mal anders machen.“*

So wird der Stil mit der Zeit nicht nur „schön“, sondern **datenbasiert**.

---

## 3. Was du Claude bei jedem neuen Video sagst (Vorlage)

```
Neues Video:
- Typ: Owner-Content / Lavish-Content
- Plattform: TikTok / Instagram Reels / YouTube Shorts
- Ziel: Reichweite / Verkauf / Vertrauen / Drop-Ankündigung
- Länge ungefähr: __ Sekunden
- Piece(s) / Thema: ___
- Musik: (Datei anbei) / keine / füge ich in der App hinzu
- Besonderheiten: ___
```

---

## 4. Technische Einrichtung (einmalig)

- **ffmpeg** ist in der Cloud-Umgebung schon installiert ✅
- **Whisper** (für automatische Transkripte/Untertitel) ist noch nicht
  installiert – Claude kann es bei Bedarf installieren. Damit es nicht jedes
  Mal neu passieren muss, kann man es in das Setup-Skript der Umgebung
  aufnehmen (sag einfach: *„Richte die Umgebung so ein, dass Whisper
  installiert ist.“*).
- Deine Fonts und dein Logo in `assets/` legen, damit Claude sie in jedem
  Video benutzen kann.

---

## 5. Kurzfassung

1. `lavish-brand` ausfüllen (Brand, Farben, Fonts, Logo)
2. Gute + schlechte Referenzvideos mit Zahlen in `beispiele/`
3. Claude die Beispiele analysieren lassen → Skills werden gefüllt
4. Test-Edits + konkretes Feedback → immer „Speicher das als Regel“
5. Performance-Zahlen zurückgeben → Stil wird immer besser

Je mehr echte Beispiele und konkretes Feedback du gibst, desto besser wird es.
