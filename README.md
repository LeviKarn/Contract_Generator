# Vertragsgenerator – MVP

## Ordnerstruktur

- `input/Contract_Generator.xlsx` – Excel-Eingabemaske
- `templates/Rahmenvertrag_Template.docx` – Word-Template mit `{{ ... }}`-Platzhaltern
- `output/` – hier werden die erzeugten Verträge gespeichert
- `src/generator.py` – Python-Logik des Generators
- `requirements.txt` – benötigte Python-Pakete
- `start_windows.bat` – späterer Start per Doppelklick unter Windows
- `start_mac.command` – späterer Start per Doppelklick unter macOS

## MVP-Logik

1. Excel-Datei aus `input/` einlesen.
2. Werte aus Spalte B anhand der technischen Feldnamen in Spalte D zuordnen.
3. Word-Template aus `templates/` befüllen.
4. Ergebnis als DOCX in `output/` speichern.
5. Dateiname aus der Rahmenvertragsnummer bilden.

Pflichtfeldprüfungen sind für die erste Version nicht vorgesehen.
