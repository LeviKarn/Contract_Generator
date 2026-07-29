from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from generator import DOCUMENT_TYPES, OUTPUT_DIR, get_fields_for_document, open_folder, render_contract


APP_TITLE = "Contract Generator"

COLORS = {
    "bg": "#f5f6f8",
    "surface": "#ffffff",
    "surface_alt": "#fafafa",
    "card": "#ffffff",
    "input": "#ffffff",
    "yellow": "#ffd21f",
    "yellow_hover": "#efc30f",
    "text": "#151515",
    "muted": "#697077",
    "line": "#dfe3e8",
    "line_strong": "#c9ced6",
    "dark": "#151515",
    "dark_hover": "#2a2a2a",
    "danger": "#b42318",
    "success": "#027a48",
    "success_bg": "#ecfdf3",
    "error_bg": "#fef3f2",
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
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry("960x760")
        self.minsize(720, 620)
        self.configure(fg_color=COLORS["bg"])

        self.status_var = tk.StringVar(value="Bereit.")
        self.active_document_type = next(iter(DOCUMENT_TYPES))
        self.fields_by_document = {}
        self.entries_by_document = {}
        self.form_frames = {}
        self.tab_buttons = {}

        self._build_ui()
        self._load_fields()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_document_area()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=36, pady=(30, 18))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Vertragsgenerator",
            text_color=COLORS["text"],
            font=("Segoe UI", 30, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew")

        badge = ctk.CTkLabel(
            header,
            text="encentive",
            text_color=COLORS["text"],
            fg_color=COLORS["yellow"],
            corner_radius=999,
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=7,
        )
        badge.grid(row=0, column=1, sticky="e")

    def _build_document_area(self):
        shell = ctk.CTkFrame(self, fg_color="transparent")
        shell.grid(row=1, column=0, sticky="nsew", padx=36)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        tab_row = ctk.CTkFrame(shell, fg_color="transparent")
        tab_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        for index, (document_type, config) in enumerate(DOCUMENT_TYPES.items()):
            tab_row.grid_columnconfigure(index, weight=1)
            tab_button = ctk.CTkButton(
                tab_row,
                text=config["label"],
                command=lambda item=document_type: self.select_document(item),
                height=58,
                corner_radius=18,
                font=("Segoe UI", 14, "bold"),
                anchor="w",
            )
            tab_button.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=(0, 10) if index == 0 else (10, 0),
            )
            self.tab_buttons[document_type] = tab_button

        panel = ctk.CTkFrame(
            shell,
            fg_color=COLORS["surface"],
            corner_radius=24,
            border_width=1,
            border_color=COLORS["line"],
        )
        panel.grid(row=1, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        panel_header = ctk.CTkFrame(panel, fg_color="transparent")
        panel_header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        panel_header.grid_columnconfigure(0, weight=1)

        self.panel_title = ctk.CTkLabel(
            panel_header,
            text="",
            text_color=COLORS["text"],
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        )
        self.panel_title.grid(row=0, column=0, sticky="ew")

        self.field_count_label = ctk.CTkLabel(
            panel_header,
            text="",
            text_color=COLORS["muted"],
            fg_color=COLORS["surface_alt"],
            corner_radius=999,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=6,
        )
        self.field_count_label.grid(row=0, column=1, sticky="e")

        self.form_container = ctk.CTkFrame(panel, fg_color="transparent")
        self.form_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 14))
        self.form_container.grid_columnconfigure(0, weight=1)
        self.form_container.grid_rowconfigure(0, weight=1)

        for document_type in DOCUMENT_TYPES:
            form_frame = ctk.CTkScrollableFrame(
                self.form_container,
                fg_color="transparent",
                scrollbar_button_color="#c8ced6",
                scrollbar_button_hover_color=COLORS["yellow"],
                corner_radius=0,
            )
            form_frame.grid(row=0, column=0, sticky="nsew")
            form_frame.grid_columnconfigure(0, weight=1)
            self.form_frames[document_type] = form_frame

        self._refresh_document_view()

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=36, pady=(18, 28))
        footer.grid_columnconfigure(0, weight=2)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)

        self.primary_button = ctk.CTkButton(
            footer,
            text="Dokument erzeugen",
            command=self.generate_current_document,
            height=50,
            corner_radius=16,
            fg_color=COLORS["yellow"],
            hover_color=COLORS["yellow_hover"],
            text_color=COLORS["text"],
            font=("Segoe UI", 13, "bold"),
        )
        self.primary_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        output_button = ctk.CTkButton(
            footer,
            text="Output öffnen",
            command=self.open_output,
            height=50,
            corner_radius=16,
            fg_color=COLORS["surface"],
            hover_color="#eef0f3",
            border_width=1,
            border_color=COLORS["line"],
            text_color=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        output_button.grid(row=0, column=1, sticky="ew", padx=10)

        reload_button = ctk.CTkButton(
            footer,
            text="Felder neu laden",
            command=self.reload_fields,
            height=50,
            corner_radius=16,
            fg_color=COLORS["surface"],
            hover_color="#eef0f3",
            border_width=1,
            border_color=COLORS["line"],
            text_color=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        reload_button.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        self.status_shell = ctk.CTkFrame(
            footer,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["line"],
        )
        self.status_shell.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))
        self.status_shell.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_shell,
            textvariable=self.status_var,
            text_color=COLORS["muted"],
            font=("Segoe UI", 11),
            anchor="w",
            padx=14,
            pady=12,
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

    def _load_fields(self):
        for document_type in DOCUMENT_TYPES:
            try:
                self.fields_by_document[document_type] = get_fields_for_document(document_type)
            except Exception as error:
                self._set_status("Felder konnten nicht geladen werden.", error=True)
                messagebox.showerror(APP_TITLE, str(error))
                return

            self._render_fields(document_type)

        self._refresh_document_view()
        self._set_status(f"{self._current_document_label()}: bereit.")

    def _render_fields(self, document_type):
        form_frame = self.form_frames[document_type]

        for child in form_frame.winfo_children():
            child.destroy()

        self.entries_by_document[document_type] = {}
        fields = self.fields_by_document[document_type]

        if not fields:
            empty = ctk.CTkLabel(
                form_frame,
                text="Keine passenden Platzhalter im Template gefunden.",
                text_color=COLORS["muted"],
                font=("Segoe UI", 12),
            )
            empty.grid(row=0, column=0, sticky="ew", pady=24)
            return

        for index in range(2):
            form_frame.grid_columnconfigure(index, weight=1, uniform="fields")

        for index, field in enumerate(fields):
            self._render_field(form_frame, document_type, index, field)

    def _render_field(self, parent, document_type, index, field):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["line"],
        )
        row_index = index // 2
        column_index = index % 2
        card.grid(
            row=row_index,
            column=column_index,
            sticky="nsew",
            padx=(10, 6) if column_index == 0 else (6, 10),
            pady=(0, 10),
        )
        card.grid_columnconfigure(0, weight=1)

        label_text = field["label"] or field["technical_name"]
        label = ctk.CTkLabel(
            card,
            text=label_text,
            text_color=COLORS["text"],
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        )
        label.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 0))

        entry = ctk.CTkEntry(
            card,
            height=36,
            corner_radius=12,
            fg_color=COLORS["input"],
            border_color=COLORS["line_strong"],
            border_width=1,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["muted"],
            font=("Segoe UI", 13),
        )
        entry.grid(row=1, column=0, sticky="ew", padx=14, pady=(6, 0))
        entry.insert(0, field["default"])

        helper_parts = []
        if field["example"]:
            helper_parts.append(f"Beispiel: {field['example']}")
        if field["hint"]:
            helper_parts.append(field["hint"])

        helper_text = " / ".join(helper_parts) if helper_parts else field["technical_name"]
        helper = ctk.CTkLabel(
            card,
            text=helper_text,
            text_color=COLORS["muted"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=390,
        )
        helper.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 10))

        self.entries_by_document[document_type][field["technical_name"]] = entry

        if index == 0 and document_type == self.active_document_type:
            entry.focus_set()

    def select_document(self, document_type):
        self.active_document_type = document_type
        self._refresh_document_view()
        field_count = len(self.fields_by_document.get(document_type, []))
        self._set_status(f"{self._current_document_label()}: {field_count} Felder bereit.")

    def _refresh_document_view(self):
        for document_type, frame in self.form_frames.items():
            if document_type == self.active_document_type:
                frame.grid()
            else:
                frame.grid_remove()

        for document_type, button in self.tab_buttons.items():
            active = document_type == self.active_document_type
            button.configure(
                fg_color=COLORS["yellow"] if active else COLORS["surface"],
                hover_color=COLORS["yellow_hover"] if active else "#eef0f3",
                text_color=COLORS["text"],
                border_width=0 if active else 1,
                border_color=COLORS["line"],
            )

        document_label = self._current_document_label()
        field_count = len(self.fields_by_document.get(self.active_document_type, []))
        self.panel_title.configure(text=f"{document_label} Daten")
        self.field_count_label.configure(text=f"{field_count} Felder")
        if hasattr(self, "primary_button"):
            self.primary_button.configure(text=f"{document_label} erzeugen")

    def reload_fields(self):
        self._load_fields()

    def _current_document_type(self):
        return self.active_document_type

    def _current_document_label(self):
        return DOCUMENT_TYPES[self.active_document_type]["label"]

    def collect_contract_data(self, document_type):
        return {
            technical_name: entry.get().strip()
            for technical_name, entry in self.entries_by_document[document_type].items()
        }

    def generate_current_document(self):
        document_type = self._current_document_type()
        document_label = DOCUMENT_TYPES[document_type]["label"]

        try:
            self._set_status(f"{document_label} wird erzeugt ...")
            self.update_idletasks()
            output_file, _ = render_contract(
                self.collect_contract_data(document_type),
                open_output=True,
                document_type=document_type,
            )
        except Exception as error:
            self._set_status("Fehler bei der Dokumenterstellung.", error=True)
            messagebox.showerror(APP_TITLE, str(error))
            return

        self._set_status(f"Erstellt: {output_file.name}", success=True)
        messagebox.showinfo(APP_TITLE, f"Dokument erfolgreich erstellt:\n{output_file}")

    def open_output(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        open_folder(OUTPUT_DIR)

    def _set_status(self, text, success=False, error=False):
        self.status_var.set(text)

        if error:
            self.status_shell.configure(fg_color=COLORS["error_bg"])
            self.status_label.configure(text_color=COLORS["danger"])
            return

        if success:
            self.status_shell.configure(fg_color=COLORS["success_bg"])
            self.status_label.configure(text_color=COLORS["success"])
            return

        self.status_shell.configure(fg_color=COLORS["surface"])
        self.status_label.configure(text_color=COLORS["muted"])


if __name__ == "__main__":
    app = ContractGeneratorApp()
    app.mainloop()
