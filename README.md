# Vertragsgenerator

## Ordnerstruktur

- `input/Contract_Generator.xlsx` - Excel-Eingabemaske
- `templates/Rahmenvertrag_Template.docx` - Word-Template mit `{{ ... }}`-Platzhaltern
- `output/` - hier werden die erzeugten Vertraege gespeichert
- `src/generator.py` - Python-Logik des Generators
- `src/app.py` - kleine Desktop-Oberflaeche
- `build_windows.bat` - baut die Windows-App
- `start_windows.bat` - Start per Doppelklick waehrend der Entwicklung
- `start_mac.command` - Start per Doppelklick unter macOS waehrend der Entwicklung

## Nutzung fuer Account Executives

Die fertige Windows-App liegt nach dem Build unter:

`dist/Contract_Generator/Contract_Generator.exe`

Der komplette Ordner `dist/Contract_Generator/` kann geteilt werden. Nutzer muessen kein Python installieren. Sie starten `Contract_Generator.exe`, tragen die Vertragsdaten direkt im Tool ein und finden den erzeugten Vertrag anschliessend im Ordner `output/`.

Die Excel-Datei im Ordner `input/` dient nur noch als Felddefinition fuer das Tool:

- Spalte A: sichtbare Feldbezeichnung
- Spalte B: vorausgefuellter Startwert
- Spalte C: Beispiel
- Spalte D: technischer Platzhaltername
- Spalte E: optionaler Hinweis

## Logik

1. Felddefinitionen aus `input/Contract_Generator.xlsx` einlesen.
2. Eingabeformular in der App dynamisch erzeugen.
3. Formularwerte anhand der technischen Feldnamen zuordnen.
4. Word-Template aus `templates/` befuellen.
5. Ergebnis als DOCX in `output/` speichern.
6. Dateiname aus der Rahmenvertragsnummer bilden.
7. Output-Ordner automatisch oeffnen.

Pflichtfeldpruefungen sind fuer die erste Version nicht vorgesehen.

## Windows-App bauen

Auf dem Build-Rechner einmalig Abhaengigkeiten installieren:

```bash
pip install -r requirements.txt
```

Danach:

```bash
build_windows.bat
```
