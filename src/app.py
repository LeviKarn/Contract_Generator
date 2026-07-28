from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from generator import EXCEL_FILE, OUTPUT_DIR, generate_contract, open_folder


APP_TITLE = "Contract Generator"


def open_file(path):
    path = Path(path)

    if not path.exists():
        messagebox.showerror(APP_TITLE, f"Datei nicht gefunden:\n{path}")
        return

    if sys.platform.startswith("win"):
        os.startfile(path)
        return

    if sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
        return

    subprocess.run(["xdg-open", str(path)], check=False)


class ContractGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("520x300")
        self.minsize(480, 280)
        self.configure(bg="#f6f7f9")

        self.status_var = tk.StringVar(value="Bereit.")

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg="#f6f7f9", padx=28, pady=24)
        container.pack(fill="both", expand=True)

        title = tk.Label(
            container,
            text="Vertragsgenerator",
            bg="#f6f7f9",
            fg="#162033",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        )
        title.pack(fill="x")

        subtitle = tk.Label(
            container,
            text="Excel ausfuellen, Vertrag erzeugen, fertige Datei im Output-Ordner abholen.",
            bg="#f6f7f9",
            fg="#536070",
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=460,
            justify="left",
        )
        subtitle.pack(fill="x", pady=(6, 20))

        primary = tk.Button(
            container,
            text="Vertrag erzeugen",
            command=self.generate,
            bg="#0f766e",
            fg="white",
            activebackground="#115e59",
            activeforeground="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=14,
            pady=12,
            cursor="hand2",
        )
        primary.pack(fill="x")

        button_row = tk.Frame(container, bg="#f6f7f9")
        button_row.pack(fill="x", pady=(14, 18))

        secondary_style = {
            "bg": "#ffffff",
            "fg": "#162033",
            "activebackground": "#e9edf2",
            "activeforeground": "#162033",
            "font": ("Segoe UI", 10),
            "relief": "solid",
            "bd": 1,
            "padx": 10,
            "pady": 9,
            "cursor": "hand2",
        }

        tk.Button(
            button_row,
            text="Excel-Vorlage oeffnen",
            command=lambda: open_file(EXCEL_FILE),
            **secondary_style,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(
            button_row,
            text="Output-Ordner oeffnen",
            command=self.open_output,
            **secondary_style,
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        status = tk.Label(
            container,
            textvariable=self.status_var,
            bg="#eef2f6",
            fg="#344054",
            font=("Segoe UI", 10),
            anchor="w",
            padx=12,
            pady=10,
            wraplength=440,
            justify="left",
        )
        status.pack(fill="x", side="bottom")

    def generate(self):
        try:
            self.status_var.set("Vertrag wird erzeugt ...")
            self.update_idletasks()
            output_file, _ = generate_contract(open_output=True)
        except Exception as error:
            self.status_var.set("Fehler bei der Vertragserstellung.")
            messagebox.showerror(APP_TITLE, str(error))
            return

        self.status_var.set(f"Erstellt: {output_file.name}")
        messagebox.showinfo(APP_TITLE, f"Vertrag erfolgreich erstellt:\n{output_file}")

    def open_output(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        open_folder(OUTPUT_DIR)


if __name__ == "__main__":
    app = ContractGeneratorApp()
    app.mainloop()
