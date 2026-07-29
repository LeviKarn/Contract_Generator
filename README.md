# Vertragsgenerator

## Ordnerstruktur

- `input/Contract_Generator.xlsx` - Excel-Eingabemaske
- `templates/Rahmenvertrag [aktuelle Version].docx` - Word-Template mit `{{ ... }}`-Platzhaltern
- `templates/Orderform_2026 [aktuelle Version_Juli].docx` - Word-Template fuer Order Forms
- `output/` - hier werden die erzeugten Vertraege gespeichert
- `src/generator.py` - Python-Logik des Generators
- `src/app.py` - kleine Desktop-Oberflaeche
- `build_windows.bat` - baut die Windows-App
- `Install_Contract_Generator.bat` - installiert die Windows-App lokal und erstellt eine Desktop-Verknuepfung
- `start_windows.bat` - Start per Doppelklick waehrend der Entwicklung
- `start_mac.command` - Start per Doppelklick unter macOS waehrend der Entwicklung

## Nutzung fuer Account Executives

Die fertige Windows-App liegt nach dem Build unter:

`dist/Contract_Generator/Contract_Generator.exe`

Der komplette Ordner `dist/Contract_Generator/` kann geteilt werden. Nutzer muessen kein Python installieren. Sie starten `Contract_Generator.exe`, waehlen den Reiter `Rahmenvertrag` oder `Order Form`, tragen die Vertragsdaten direkt im Tool ein und finden das erzeugte Dokument anschliessend im Ordner `output/`.

Der `output/`-Ordner ist nur ein temporärer Ablageort. Vor jedem neuen Dokument werden alte `.docx`-Dateien aus `output/` automatisch gelöscht. Erzeugte Dokumente sollten daher direkt in den passenden Kunden- oder Deal-Ordner kopiert werden.

## Windows-Installer fuer Kollegen

Lege diese beiden Dateien gemeinsam in SharePoint oder OneDrive ab:

- `Install_Contract_Generator.bat`
- `Contract_Generator_Windows.zip`

Kollegen starten per Doppelklick `Install_Contract_Generator.bat`. Der Installer entpackt die App nach `%LOCALAPPDATA%\Contract_Generator` und erstellt eine Desktop-Verknuepfung `Contract_Generator`.

Die App sollte lokal installiert genutzt werden, nicht direkt gemeinsam aus dem SharePoint-Ordner. So hat jeder Nutzer einen eigenen `output/`-Ordner und es gibt keine Sync-Konflikte.

Die Excel-Datei im Ordner `input/` dient nur noch als Felddefinition fuer das Tool:

- Spalte A: sichtbare Feldbezeichnung
- Spalte B: vorausgefuellter Startwert
- Spalte C: Beispiel
- Spalte D: technischer Platzhaltername
- Spalte E: optionaler Hinweis

## Logik

1. Felddefinitionen aus `input/Contract_Generator.xlsx` einlesen.
2. Platzhalter aus dem jeweiligen Word-Template erkennen.
3. Je Dokumenttyp ein passendes Eingabeformular in der App erzeugen.
4. Formularwerte anhand der technischen Feldnamen zuordnen.
5. Word-Template aus `templates/` befuellen.
6. Ergebnis als DOCX in `output/` speichern.
7. Dateiname aus Rahmenvertragsnummer oder Order-Form-Nummer bilden.
8. Output-Ordner automatisch oeffnen.

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
