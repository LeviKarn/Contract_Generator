from datetime import date, datetime
from pathlib import Path
import os
import platform
import re
import subprocess
import sys

from docxtpl import DocxTemplate
from openpyxl import load_workbook


# Projektordner unabhängig vom aktuellen Speicherort bestimmen
def get_project_dir():
    """
    Determines the folder that contains input/, templates/ and output/.
    In a PyInstaller build this is the folder next to the executable.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


PROJECT_DIR = get_project_dir()

EXCEL_FILE = PROJECT_DIR / "input" / "Contract_Generator.xlsx"
TEMPLATE_FILE = PROJECT_DIR / "templates" / "Rahmenvertrag_Template.docx"
OUTPUT_DIR = PROJECT_DIR / "output"

SHEET_NAME = "Vertragsdaten"


def format_excel_value(value):
    """
    Wandelt Excel-Werte in eine für Word geeignete Darstellung um.
    """
    if value is None:
        return ""

    if isinstance(value, (datetime, date)):
        return value.strftime("%d.%m.%Y")

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value).strip()


def read_contract_data():
    """
    Liest die Eingaben aus Spalte B und ordnet sie anhand der
    technischen Feldnamen aus Spalte D zu.
    """
    workbook = load_workbook(EXCEL_FILE, data_only=True)

    if SHEET_NAME not in workbook.sheetnames:
        raise ValueError(
            f"Das Tabellenblatt '{SHEET_NAME}' wurde nicht gefunden."
        )

    worksheet = workbook[SHEET_NAME]
    contract_data = {}

    # Zeile 1 enthält die Überschriften
    for row in range(2, worksheet.max_row + 1):
        input_value = worksheet.cell(row=row, column=2).value
        technical_field_name = worksheet.cell(row=row, column=4).value

        if technical_field_name is None:
            continue

        technical_field_name = str(technical_field_name).strip()

        if not technical_field_name:
            continue

        contract_data[technical_field_name] = format_excel_value(input_value)

    return contract_data


def sanitize_filename(filename):
    """
    Entfernt Zeichen, die unter Windows oder macOS nicht in
    Dateinamen verwendet werden sollten.
    """
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = filename.strip().strip(".")
    return filename or "Rahmenvertrag_generiert"


def open_folder(folder_path):
    """
    Opens a folder in the user's file browser.
    """
    folder_path = Path(folder_path)

    if platform.system() == "Windows":
        os.startfile(folder_path)
        return

    if platform.system() == "Darwin":
        subprocess.run(["open", str(folder_path)], check=False)
        return

    subprocess.run(["xdg-open", str(folder_path)], check=False)


def generate_contract(open_output=False):
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Excel-Datei nicht gefunden:\n{EXCEL_FILE}"
        )

    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(
            f"Word-Template nicht gefunden:\n{TEMPLATE_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    contract_data = read_contract_data()

    print("\nEingelesene Vertragsdaten:")
    for field_name, value in contract_data.items():
        displayed_value = value if value else "[leer]"
        print(f"  {field_name}: {displayed_value}")

    document = DocxTemplate(TEMPLATE_FILE)
    document.render(contract_data)

    contract_number = contract_data.get("rahmenvertragsnummer", "")
    output_name = sanitize_filename(
        f"{contract_number}_Rahmenvertrag"
        if contract_number
        else "Rahmenvertrag_generiert"
    )

    output_file = OUTPUT_DIR / f"{output_name}.docx"
    document.save(output_file)

    print("\nVertrag erfolgreich erstellt:")
    print(output_file)

    if open_output:
        open_folder(OUTPUT_DIR)

    return output_file, contract_data


def main():
    try:
        generate_contract(open_output=True)
    except Exception as error:
        print("\nFEHLER BEI DER VERTRAGSERSTELLUNG")
        print("----------------------------------")
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
