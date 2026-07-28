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

Der komplette Ordner `dist/Contract_Generator/` kann geteilt werden. Nutzer muessen kein Python installieren. Sie fuellen die Excel-Datei im Ordner `input/` aus, starten `Contract_Generator.exe` und finden den erzeugten Vertrag anschliessend im Ordner `output/`.

## Logik

1. Excel-Datei aus `input/` einlesen.
2. Werte aus Spalte B anhand der technischen Feldnamen in Spalte D zuordnen.
3. Word-Template aus `templates/` befuellen.
4. Ergebnis als DOCX in `output/` speichern.
5. Dateiname aus der Rahmenvertragsnummer bilden.
6. Output-Ordner automatisch oeffnen.

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
