---
name: real-mockups-lavish
description: „Real Mockups Lavish“ – Designs des Owners (T-Shirts, Beanies, Hoodies, Tracksuits …) fotorealistisch visualisieren, bevor das echte Produkt existiert, für Website und Instagram. Verwenden, sobald der Owner ein Design schickt, das als realistisches Produktbild dargestellt werden soll.
---

# Real Mockups Lavish

## Ziel
Der Owner schickt eigene Designs. Daraus entstehen **fotorealistische Produktbilder**, die auf der
Website und auf Instagram genutzt werden, bevor das Piece physisch da ist. Das Bild muss so aussehen,
wie das Produkt **in echt** aussehen wird. Jedes Detail muss stimmen, nichts wird dazuerfunden.

## Referenz-Look (vom Owner geschickt, Nov. 2026)
`mockups/referenzen/` – zwei Beispiel-Tees (Fremd-Designs, nur als Stil-Referenz):
- Freigestelltes Produkt, **flach/frontal („Ghost“/Flatlay-Look)**, heller neutraler Hintergrund, weicher Schatten.
- Echte Stoffstruktur, Falten, Nähte und Kragenrippe; der Print folgt den Falten und hat Wash und Abrieb.
- Washed/Vintage-Look möglich: Ausbleichen, Distressing, Löcher.

## Ablauf
1. Design-Datei(en) annehmen und unter `mockups/<produkt-name>/design/` ablegen.
2. **Detail-Checkliste** (unten) mit dem Owner durchgehen. Was fehlt, wird nachgefragt und nicht geraten.
3. Visualisieren:
   - **Weg A – Compositing (hier im Repo, Python/PIL/ImageMagick):** Design auf ein echtes,
     leeres Produktfoto (Blank) legen, mit Displacement nach den Falten, Licht/Schatten übernehmen,
     Stofftextur und bei Bedarf Wash. Das Ergebnis ist exakt treu zum Design. Dafür wird ein gutes Blank-Foto gebraucht.
   - **Weg B – Bild-KI-Prompt:** präziser Prompt + Design als Referenzbild für ein Bildmodell
     (z. B. ChatGPT-Bilder, Gemini, Midjourney), das der Owner ausführt. Liefert mehr Realismus und Szenen,
     erfindet aber gern Details. Deshalb jedes Ergebnis gegen die Checkliste prüfen.
4. Ergebnis unter `mockups/<produkt-name>/` speichern und Abweichungen ehrlich benennen.

## Detail-Checkliste (pro Produkt)
**Allgemein:** Produktart, Schnitt/Fit, Grundfarbe (Hex oder Pantone, sonst Foto), Material/Stoffgewicht,
Wash/Distressing ja/nein, Ansicht(en) (vorne/hinten/seitlich/getragen), Hintergrund, Bildformat
(Website z. B. 1:1 / 4:5, Instagram 4:5).
**Veredelung pro Motiv:** Siebdruck / DTG / Puff-Print / Stick / Patch / Jacquard (eingestrickt) /
Label; Position und Größe in cm; Farben des Motivs.
**Beanie zusätzlich:** Strickart (Rippe fein/grob, Waffel, Jersey), mit oder ohne Umschlag (Cuff) und dessen Höhe,
Höhe gesamt (Short/Fisherman vs. normal), Bommel ja/nein, Logo als Stick, gewebtes Label, Patch oder
Jacquard, Position (mittig vorne auf dem Cuff? seitlich?), Garn-/Fadenfarbe, Außenlabel/Tag.
**T-Shirt zusätzlich:** Boxy/oversized/regular, Kragenbreite, Ärmellänge, Saum (roh/offen?), Print vorne/hinten.

## No-Gos
- Keine geschützten Figuren, Logos oder Marken anderer in Lavish-Designs (Hinweis geben, falls vorhanden).
- Keine erfundenen Details (Extra-Labels, falsche Schrift, andere Farben).
- Mockup nicht als echtes Foto ausgeben, wenn das Produkt anders ausfallen wird.

## Gelernte Regeln
- **Lavish-Beanie-Blank (Drop 26):** dünner, feiner Rippstrick, ohne Umschlag, flache Dome-Form; flach gelegt fotografiert.
  „Schwarz“ = **Washed Black** (leicht ausgewaschen, kühler Grauton, ca. RGB 36/38/42). Prints sitzen als Druck auf den Rippen.
- Der Owner fotografiert Pieces auf **hellen Sprenkel-Fliesen**. Neben dem Studio-Shot immer auch eine Fliesen-Version liefern,
  die zu den echten Fotos des Owners passt.
- Werkzeug: `mockups/beanies-drop-26/` enthält Ausgangsfotos, Designs und Ergebnisse. Ablauf: echte Silhouette aus dem Foto
  freistellen, Rippstrick prozedural nachbauen, Design auf die Bounding-Box der Silhouette mappen.
- **„LAVSH“ ohne I auf der weißen Beanie (Drop 26) ist gewollt.** Nicht korrigieren und nicht erneut nachfragen.
  Generell gilt: Schreibweisen im Design 1:1 übernehmen. Höchstens einmal nachfragen, nie eigenmächtig ändern.
- **Standard-Hintergrund für Produktbilder (vom Owner festgelegt, Nov. 2026):** flaches, neutrales Hellgrau
  wie die Lavish-Flanell-Referenz (ca. RGB 229/228/228, unten minimal dunkler), weicher Schatten unter dem Piece,
  Format 3:4, Piece mittig, ca. 64 % Bildbreite. **Jedes Piece als einzelnes Bild** liefern. Freigestellte PNGs nur zusätzlich.
- **Realismus-Anspruch (Owner, Nov. 2026):** Kleidung mit Falten (Hoodies, Shirts) muss **fotoecht** aussehen, wie ein echtes
  Produktfoto mit Ghost-Mannequin. Prozedurales Rendering reicht dafür **nicht**. Es geht nur für flache Teile wie Beanies.
  Für Hoodies und Shirts deshalb: (a) echtes Blank-Foto des Owners bzw. Herstellers + Compositing, oder (b) Bild-KI-Prompt
  (`mockups/hoodie-lavish-collective-24/KI-PROMPT.md` als Vorlage), oder (c) Bild-API direkt, wenn der Owner einen Key hinterlegt.
  Fremde Produktfotos anderer Brands nur als Stil-Referenz verwenden, nie als Bildbasis.
