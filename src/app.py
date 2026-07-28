from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from generator import OUTPUT_DIR, open_folder, read_field_definitions, render_contract


APP_TITLE = "Contract Generator"

COLORS = {
    "bg": "#0b0b0f",
    "panel": "#15161b",
    "panel_alt": "#1d1f26",
    "input": "#101116",
    "input_hover": "#181a20",
    "yellow": "#ffd21f",
    "yellow_hover": "#e7bd12",
    "yellow_pressed": "#cfa80c",
    "text": "#f6f4ea",
    "muted": "#aaa99f",
    "line": "#2b2d35",
    "danger": "#ff6b5f",
    "success": "#85e89d",
}


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


class ContractGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_TITLE)
        self.geometry("820x780")
        self.minsize(680, 600)
        self.configure(fg_color=COLORS["bg"])

        self.status_var = tk.StringVar(value="Bereit.")
        self.fields = []
        self.entries = {}

        self._build_ui()
        self._load_fields()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_form_panel()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=34, pady=(28, 18))
        header.grid_columnconfigure(0, weight=1)

        brand = ctk.CTkFrame(
            header,
            fg_color=COLORS["yellow"],
            corner_radius=16,
            width=54,
            height=54,
        )
        brand.grid(row=0, column=0, sticky="w")
        brand.grid_propagate(False)

        brand_label = ctk.CTkLabel(
            brand,
            text="e",
            text_color="#111111",
            font=("Segoe UI", 25, "bold"),
        )
        brand_label.place(relx=0.5, rely=0.48, anchor="center")

        title_stack = ctk.CTkFrame(header, fg_color="transparent")
        title_stack.grid(row=0, column=0, sticky="ew", padx=(72, 0))
        title_stack.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            title_stack,
            text="Vertragsgenerator",
            text_color=COLORS["text"],
            font=("Segoe UI", 28, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew")

        subtitle = ctk.CTkLabel(
            title_stack,
            text="Schnell erfassen. Sauber erzeugen. Direkt im Output-Ordner abholen.",
            text_color=COLORS["muted"],
            font=("Segoe UI", 12),
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        badge = ctk.CTkLabel(
            header,
            text="encentive",
            text_color=COLORS["yellow"],
            fg_color=COLORS["panel_alt"],
            corner_radius=999,
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=7,
        )
        badge.grid(row=0, column=1, sticky="e")

    def _build_form_panel(self):
        shell = ctk.CTkFrame(self, fg_color="transparent")
        shell.grid(row=1, column=0, sticky="nsew", padx=34)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(
            shell,
            fg_color=COLORS["panel"],
            corner_radius=24,
            border_width=1,
            border_color=COLORS["line"],
        )
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        panel_header = ctk.CTkFrame(panel, fg_color="transparent")
        panel_header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 12))
        panel_header.grid_columnconfigure(0, weight=1)

        panel_title = ctk.CTkLabel(
            panel_header,
            text="Vertragsdaten",
            text_color=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        panel_title.grid(row=0, column=0, sticky="ew")

        self.field_count_label = ctk.CTkLabel(
            panel_header,
            text="",
            text_color=COLORS["yellow"],
            fg_color=COLORS["input"],
            corner_radius=999,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=6,
        )
        self.field_count_label.grid(row=0, column=1, sticky="e")

        self.form_frame = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_button_color="#343741",
            scrollbar_button_hover_color=COLORS["yellow"],
            corner_radius=0,
        )
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 14))
        self.form_frame.grid_columnconfigure(0, weight=1)

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=34, pady=(18, 28))
        footer.grid_columnconfigure(0, weight=2)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)

        primary = ctk.CTkButton(
            footer,
            text="Vertrag erzeugen",
            command=self.generate_from_form,
            height=48,
            corner_radius=18,
            fg_color=COLORS["yellow"],
            hover_color=COLORS["yellow_hover"],
            text_color="#111111",
            font=("Segoe UI", 13, "bold"),
        )
        primary.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        output_button = ctk.CTkButton(
            footer,
            text="Output öffnen",
            command=self.open_output,
            height=48,
            corner_radius=18,
            fg_color=COLORS["panel_alt"],
            hover_color="#282b33",
            text_color=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        output_button.grid(row=0, column=1, sticky="ew", padx=10)

        reload_button = ctk.CTkButton(
            footer,
            text="Felder neu laden",
            command=self.reload_fields,
            height=48,
            corner_radius=18,
            fg_color=COLORS["panel_alt"],
            hover_color="#282b33",
            text_color=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        reload_button.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        status_shell = ctk.CTkFrame(
            footer,
            fg_color=COLORS["panel"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["line"],
        )
        status_shell.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))
        status_shell.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_shell,
            textvariable=self.status_var,
            text_color=COLORS["muted"],
            font=("Segoe UI", 11),
            anchor="w",
            padx=14,
            pady=12,
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

    def _load_fields(self):
        try:
            self.fields = read_field_definitions()
        except Exception as error:
            self._set_status("Felder konnten nicht geladen werden.", error=True)
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._render_fields()
        self.field_count_label.configure(text=f"{len(self.fields)} Felder")
        self._set_status(f"{len(self.fields)} Felder geladen.")

    def _render_fields(self):
        for child in self.form_frame.winfo_children():
            child.destroy()

        self.entries = {}

        if not self.fields:
            empty = ctk.CTkLabel(
                self.form_frame,
                text="Keine Felder gefunden.",
                text_color=COLORS["muted"],
                font=("Segoe UI", 12),
            )
            empty.grid(row=0, column=0, sticky="ew", pady=24)
            return

        for index, field in enumerate(self.fields):
            self._render_field(index, field)

    def _render_field(self, index, field):
        card = ctk.CTkFrame(
            self.form_frame,
            fg_color=COLORS["panel_alt"],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["line"],
        )
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=(0, 12))
        card.grid_columnconfigure(1, weight=1)

        number = ctk.CTkLabel(
            card,
            text=f"{index + 1:02d}",
            text_color="#111111",
            fg_color=COLORS["yellow"],
            corner_radius=12,
            font=("Segoe UI", 11, "bold"),
            width=42,
            height=32,
        )
        number.grid(row=0, column=0, sticky="nw", padx=(16, 12), pady=16)

        label_text = field["label"] or field["technical_name"]
        label = ctk.CTkLabel(
            card,
            text=label_text,
            text_color=COLORS["text"],
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        )
        label.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=(14, 0))

        entry = ctk.CTkEntry(
            card,
            height=42,
            corner_radius=14,
            fg_color=COLORS["input"],
            border_color="#3a3d46",
            border_width=1,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["muted"],
            font=("Segoe UI", 13),
        )
        entry.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=(8, 0))
        entry.insert(0, field["default"])

        helper_parts = []
        if field["example"]:
            helper_parts.append(f"Beispiel: {field['example']}")
        if field["hint"]:
            helper_parts.append(field["hint"])

        helper_text = " · ".join(helper_parts) if helper_parts else field["technical_name"]
        helper = ctk.CTkLabel(
            card,
            text=helper_text,
            text_color=COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            wraplength=610,
        )
        helper.grid(row=2, column=1, sticky="ew", padx=(0, 16), pady=(6, 16))

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
            self._set_status("Vertrag wird erzeugt ...")
            self.update_idletasks()
            output_file, _ = render_contract(
                self.collect_contract_data(),
                open_output=True,
            )
        except Exception as error:
            self._set_status("Fehler bei der Vertragserstellung.", error=True)
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._set_status(f"Erstellt: {output_file.name}", success=True)
        messagebox.showinfo(APP_TITLE, f"Vertrag erfolgreich erstellt:\n{output_file}")

    def open_output(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        open_folder(OUTPUT_DIR)

    def _set_status(self, text, success=False, error=False):
        self.status_var.set(text)

        if error:
            self.status_label.configure(text_color=COLORS["danger"])
            return

        if success:
            self.status_label.configure(text_color=COLORS["success"])
            return

        self.status_label.configure(text_color=COLORS["muted"])


if __name__ == "__main__":
    app = ContractGeneratorApp()
    app.mainloop()
