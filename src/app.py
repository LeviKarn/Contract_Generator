from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from generator import (
    EXCEL_FILE,
    OUTPUT_DIR,
    generate_contract,
    open_folder,
    read_field_definitions,
    render_contract,
)


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
        self.geometry("680x720")
        self.minsize(560, 520)
        self.configure(bg="#f6f7f9")

        self.status_var = tk.StringVar(value="Bereit.")
        self.fields = []
        self.entries = {}

        self._build_ui()
        self._load_fields()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#f6f7f9", padx=28, pady=22)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text="Vertragsgenerator",
            bg="#f6f7f9",
            fg="#162033",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew")

        subtitle = tk.Label(
            header,
            text="Vertragsdaten eintragen und Vertrag erzeugen. Excel dient nur noch als Felddefinition.",
            bg="#f6f7f9",
            fg="#536070",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        subtitle.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        form_shell = tk.Frame(self, bg="#f6f7f9", padx=28)
        form_shell.grid(row=1, column=0, sticky="nsew")
        form_shell.columnconfigure(0, weight=1)
        form_shell.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            form_shell,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d8dee8",
        )
        scrollbar = tk.Scrollbar(form_shell, orient="vertical", command=self.canvas.yview)
        self.form_frame = tk.Frame(self.canvas, bg="#ffffff", padx=18, pady=18)

        self.form_window = self.canvas.create_window(
            (0, 0),
            window=self.form_frame,
            anchor="nw",
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.form_frame.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_form_width)

        footer = tk.Frame(self, bg="#f6f7f9", padx=28, pady=18)
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)
        footer.columnconfigure(2, weight=1)

        primary = tk.Button(
            footer,
            text="Vertrag erzeugen",
            command=self.generate_from_form,
            bg="#0f766e",
            fg="white",
            activebackground="#115e59",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=14,
            pady=11,
            cursor="hand2",
        )
        primary.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        secondary_style = {
            "bg": "#ffffff",
            "fg": "#162033",
            "activebackground": "#e9edf2",
            "activeforeground": "#162033",
            "font": ("Segoe UI", 10),
            "relief": "solid",
            "bd": 1,
            "padx": 10,
            "pady": 10,
            "cursor": "hand2",
        }

        tk.Button(
            footer,
            text="Output oeffnen",
            command=self.open_output,
            **secondary_style,
        ).grid(row=0, column=1, sticky="ew", padx=8)

        tk.Button(
            footer,
            text="Felder neu laden",
            command=self.reload_fields,
            **secondary_style,
        ).grid(row=0, column=2, sticky="ew", padx=(8, 0))

        status = tk.Label(
            footer,
            textvariable=self.status_var,
            bg="#eef2f6",
            fg="#344054",
            font=("Segoe UI", 10),
            anchor="w",
            padx=12,
            pady=10,
            wraplength=600,
            justify="left",
        )
        status.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))

    def _sync_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_form_width(self, event):
        self.canvas.itemconfigure(self.form_window, width=event.width)

    def _load_fields(self):
        try:
            self.fields = read_field_definitions()
        except Exception as error:
            self.status_var.set("Felder konnten nicht geladen werden.")
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._render_fields()
        self.status_var.set(f"{len(self.fields)} Felder geladen.")

    def _render_fields(self):
        for child in self.form_frame.winfo_children():
            child.destroy()

        self.entries = {}

        if not self.fields:
            tk.Label(
                self.form_frame,
                text="Keine Felder gefunden.",
                bg="#ffffff",
                fg="#344054",
                font=("Segoe UI", 10),
                anchor="w",
            ).pack(fill="x")
            return

        for index, field in enumerate(self.fields):
            row = tk.Frame(self.form_frame, bg="#ffffff")
            row.pack(fill="x", pady=(0, 16))
            row.columnconfigure(0, weight=1)

            label_text = field["label"] or field["technical_name"]
            label = tk.Label(
                row,
                text=label_text,
                bg="#ffffff",
                fg="#162033",
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            )
            label.grid(row=0, column=0, sticky="ew")

            entry = tk.Entry(
                row,
                bg="#ffffff",
                fg="#162033",
                insertbackground="#162033",
                font=("Segoe UI", 11),
                relief="solid",
                bd=1,
            )
            entry.grid(row=1, column=0, sticky="ew", ipady=7, pady=(5, 0))
            entry.insert(0, field["default"])

            helper_parts = []
            if field["example"]:
                helper_parts.append(f"Beispiel: {field['example']}")
            if field["hint"]:
                helper_parts.append(field["hint"])

            if helper_parts:
                helper = tk.Label(
                    row,
                    text=" | ".join(helper_parts),
                    bg="#ffffff",
                    fg="#667085",
                    font=("Segoe UI", 9),
                    anchor="w",
                    justify="left",
                    wraplength=590,
                )
                helper.grid(row=2, column=0, sticky="ew", pady=(4, 0))

            self.entries[field["technical_name"]] = entry

            if index == 0:
                entry.focus_set()

    def reload_fields(self):
        self._load_fields()

    def collect_contract_data(self):
        return {
            technical_name: entry.get().strip()
            for technical_name, entry in self.entries.items()
        }

    def generate_from_form(self):
        try:
            self.status_var.set("Vertrag wird erzeugt ...")
            self.update_idletasks()
            output_file, _ = render_contract(
                self.collect_contract_data(),
                open_output=True,
            )
        except Exception as error:
            self.status_var.set("Fehler bei der Vertragserstellung.")
            messagebox.showerror(APP_TITLE, str(error))
            return

        self.status_var.set(f"Erstellt: {output_file.name}")
        messagebox.showinfo(APP_TITLE, f"Vertrag erfolgreich erstellt:\n{output_file}")

    def generate_from_excel(self):
        try:
            output_file, _ = generate_contract(open_output=True)
        except Exception as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self.status_var.set(f"Erstellt: {output_file.name}")

    def open_output(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        open_folder(OUTPUT_DIR)


if __name__ == "__main__":
    app = ContractGeneratorApp()
    app.mainloop()
