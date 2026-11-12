---
name: performance-check
description: Checkliste vor dem Export, damit Lavish- und Owner-Videos performen (Hook, Retention, Loop, Caption), plus Log der echten Statistiken veröffentlichter Videos. Verwenden vor jedem Export und wenn der Owner Zahlen/Insights eines Videos teilt.
---

# Performance-Check

## PFLICHT: Selbstkontrolle, bevor der Owner irgendetwas bekommt
**Regel des Owners (12.11.2026): Kein Ergebnis schicken, bevor ich selbst ausschließen kann, dass etwas falsch ist.**
Erst wenn alle Punkte geprüft und bestanden sind, wird gesendet. Fehler vorher beheben, nicht mitliefern.
1. **Ganzes Video ansehen:** Kontaktbogen über die volle Länge (mind. 2 Bilder pro Sekunde) + jedes Bild direkt vor/nach jedem Schnitt
2. **Jede Einblendung einzeln:** Anfang, Mitte, Ende als Vollbild ansehen (lesbar? im Bild? nichts verdeckt Gesicht? richtige Farbe/Schrift?)
3. **Untertitel Wort für Wort** gegen den Ton prüfen (zweites Transkript des fertigen Videos); „Lavish“ und Namen richtig
4. **Timing:** jede Grafik erscheint auf das gesprochene Wort (± 0,15 s)
5. **Ton:** keine abgeschnittenen Wörter an Schnitten, kein Knacken, Lautheit ca. -14 LUFS, kein Clipping
6. **Technik:** 1080x1920, 30 fps, H.264 + AAC, Dauer stimmt, Datei spielt ab
7. **Safe-Zones** TikTok und Instagram-Story frei (oben 15 %, unten 25 %, rechts 15 %)
8. **Lavish-Logo am Ende** vorhanden
9. **Keine Reste:** alte Texte, Artefakte, Platzhalter, falsche Jahreszahlen, geschätzte Fakten
10. **Stil:** erwachsen, Lavish, nicht kindlich, nicht Baukasten/KI; verbotene Dinge (VHS, Whooshes, Icons) nicht drin
11. Alle Regeln aus „Gelernte Regeln“ der Skills noch einmal gegenlesen
Was sich nicht ausschließen lässt (z. B. fehlende Schrift, fehlende Fakten), wird **vor** dem Senden offen benannt oder nachgefragt.

**Als Skript:** `tools/owner-video-v2/qa.py` prüft Technik, Ton, Schnitte, Untertitel gegen den Ton, QR-Code, Safe-Zones,
Schlussbild und ob eine Grafik das Gesicht verdeckt. Zusätzlich immer selbst ansehen: Kontaktbogen (2 Bilder/s),
Bilder vor/nach jedem Schnitt, jede Einblendung in voller Größe.
**Grenze:** Claude kann das Video nicht anhören. Klang, Betonung und Gefühl prüft der Owner.

## Checkliste vor jedem Export
- [ ] Die ersten **1–2 Sekunden** stoppen den Scroll (Bewegung, Aussage oder starkes Bild – kein Logo-Intro, kein „Hey Leute“)
- [ ] Kein toter Moment > [AUSFÜLLEN, Standard 1,5] Sek.
- [ ] Untertitel lesbar und nicht von App-UI verdeckt (oben ~15 %, unten ~20 % freihalten)
- [ ] Länge passt zum Format (Owner: [AUSFÜLLEN] Sek., Lavish: [AUSFÜLLEN] Sek.)
- [ ] Ende: Loop oder klarer CTA (je nach Skill)
- [ ] **Lavish-Logo (L) am Ende vorhanden** (Pflicht bei jedem Video)
- [ ] Stil-Regeln aus `lavish-brand` eingehalten (keine No-Gos)
- [ ] Caption + Hashtags vorgeschlagen
- [ ] Ton: Stimme klar, Musik nicht zu laut, Lautheit normalisiert

## Lavish-Check (aus `LAVISH-GUIDELINES.md`, vor jedem Export)
- [ ] **Sieht es NICHT nach „mit Claude/KI geschnitten“ aus?** (keine App-Karten, Standard-Icons, Fließband-Animationen; siehe `owner-content`)
- [ ] Sieht es **nicht** aus wie ein generisches Fashion-Influencer-Reel?
- [ ] Gehört der Edit ins Lavish-Universum (Street Culture, Character, Identity, Attitude)?
- [ ] Zooms, Grafiken, Sounds sparsam, nichts ohne Grund?
- [ ] Keine CapCut-Übergänge, keine Glitches, keine Emojis?
- [ ] Grading dezent: leicht entsättigt, tiefe Schwarztöne, natürliche Haut?
- [ ] Umgebungston erhalten?
- [ ] Im Zweifel: Authentizität vor Perfektion, Atmosphäre vor Effekt

## Was bei unseren Videos funktioniert (aus echten Zahlen abgeleitet)
- (wird aus dem Log unten ergänzt)

## Was nicht funktioniert
- (wird aus dem Log unten ergänzt)

## Performance-Log
| Datum | Plattform | Typ | Thema/Hook | Länge | Views | Ø Wiedergabe | Saves | Shares | Erkenntnis |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
