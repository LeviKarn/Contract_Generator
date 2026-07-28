from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from generator import OUTPUT_DIR, open_folder, read_field_definitions, render_contract


APP_TITLE = "Contract Generator"

COLORS = {
    "background": "#eef2f6",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "border": "#d8e0ea",
    "text": "#142033",
    "muted": "#667085",
    "primary": "#0f766e",
    "primary_hover": "#115e59",
    "primary_pressed": "#134e4a",
    "accent": "#2563eb",
    "accent_soft": "#e8f0ff",
    "danger": "#b42318",
    "success_soft": "#ecfdf3",
    "success_text": "#027a48",
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


class HoverButton(tk.Button):
    def __init__(self, master, normal_bg, hover_bg, pressed_bg=None, **kwargs):
        super().__init__(
            master,
            bg=normal_bg,
            activebackground=pressed_bg or hover_bg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            **kwargs,
        )
        self.normal_bg = normal_bg
        self.hover_bg = hover_bg
        self.pressed_bg = pressed_bg or hover_bg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_enter)

    def _on_enter(self, _event=None):
        self.configure(bg=self.hover_bg)

    def _on_leave(self, _event=None):
        self.configure(bg=self.normal_bg)

    def _on_press(self, _event=None):
        self.configure(bg=self.pressed_bg)


class ContractGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x760")
        self.minsize(620, 560)
        self.configure(bg=COLORS["background"])

        self.status_var = tk.StringVar(value="Bereit.")
        self.fields = []
        self.entries = {}

        self._build_ui()
        self._load_fields()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=COLORS["background"], padx=32, pady=26)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title_row = tk.Frame(header, bg=COLORS["background"])
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.columnconfigure(0, weight=1)

        title = tk.Label(
            title_row,
            text="Vertragsgenerator",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI", 22, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew")

        badge = tk.Label(
            title_row,
            text="Windows App",
            bg=COLORS["accent_soft"],
            fg=COLORS["accent"],
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=5,
        )
        badge.grid(row=0, column=1, sticky="e")

        subtitle = tk.Label(
            header,
            text="Vertragsdaten direkt im Tool erfassen. Der fertige Vertrag landet automatisch im Output-Ordner.",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        subtitle.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        form_shell = tk.Frame(self, bg=COLORS["background"], padx=32)
        form_shell.grid(row=1, column=0, sticky="nsew")
        form_shell.columnconfigure(0, weight=1)
        form_shell.rowconfigure(0, weight=1)

        panel = tk.Frame(
            form_shell,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        panel.grid(row=0, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        panel_header = tk.Frame(panel, bg=COLORS["surface"], padx=20, pady=16)
        panel_header.grid(row=0, column=0, sticky="ew")
        panel_header.columnconfigure(0, weight=1)

        panel_title = tk.Label(
            panel_header,
            text="Vertragsdaten",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        panel_title.grid(row=0, column=0, sticky="ew")

        self.field_count_label = tk.Label(
            panel_header,
            text="",
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
            padx=10,
            pady=5,
        )
        self.field_count_label.grid(row=0, column=1, sticky="e")

        scroll_area = tk.Frame(panel, bg=COLORS["surface"])
        scroll_area.grid(row=1, column=0, sticky="nsew")
        scroll_area.columnconfigure(0, weight=1)
        scroll_area.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            scroll_area,
            bg=COLORS["surface"],
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            scroll_area,
            orient="vertical",
            command=self.canvas.yview,
            width=14,
            bd=0,
            highlightthickness=0,
        )
        self.form_frame = tk.Frame(self.canvas, bg=COLORS["surface"], padx=20, pady=4)

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
        self._bind_mousewheel(self.canvas)

        footer = tk.Frame(self, bg=COLORS["background"], padx=32, pady=20)
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=2)
        footer.columnconfigure(1, weight=1)
        footer.columnconfigure(2, weight=1)

        primary = HoverButton(
            footer,
            normal_bg=COLORS["primary"],
            hover_bg=COLORS["primary_hover"],
            pressed_bg=COLORS["primary_pressed"],
            text="Vertrag erzeugen",
            command=self.generate_from_form,
            fg="white",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=12,
        )
        primary.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        secondary_style = {
            "fg": COLORS["text"],
            "activeforeground": COLORS["text"],
            "font": ("Segoe UI", 10),
            "padx": 12,
            "pady": 12,
        }

        HoverButton(
            footer,
            normal_bg=COLORS["surface"],
            hover_bg="#eef4fb",
            pressed_bg="#e3ebf5",
            text="Output oeffnen",
            command=self.open_output,
            **secondary_style,
        ).grid(row=0, column=1, sticky="ew", padx=10)

        HoverButton(
            footer,
            normal_bg=COLORS["surface"],
            hover_bg="#eef4fb",
            pressed_bg="#e3ebf5",
            text="Felder neu laden",
            command=self.reload_fields,
            **secondary_style,
        ).grid(row=0, column=2, sticky="ew", padx=(10, 0))

        self.status_label = tk.Label(
            footer,
            textvariable=self.status_var,
            bg=COLORS["surface_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
            padx=14,
            pady=11,
            wraplength=680,
            justify="left",
        )
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))

    def _bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda _event: self._activate_mousewheel())
        widget.bind("<Leave>", lambda _event: self._deactivate_mousewheel())

    def _activate_mousewheel(self):
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def _deactivate_mousewheel(self):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            self.canvas.yview_scroll(-3, "units")
            return

        if getattr(event, "num", None) == 5:
            self.canvas.yview_scroll(3, "units")
            return

        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta * 3, "units")

    def _sync_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_form_width(self, event):
        self.canvas.itemconfigure(self.form_window, width=event.width)

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
            tk.Label(
                self.form_frame,
                text="Keine Felder gefunden.",
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                font=("Segoe UI", 10),
                anchor="w",
            ).pack(fill="x", pady=20)
            return

        for index, field in enumerate(self.fields):
            self._render_field(index, field)

    def _render_field(self, index, field):
        row = tk.Frame(self.form_frame, bg=COLORS["surface"])
        row.pack(fill="x", pady=(0, 18))
        row.columnconfigure(1, weight=1)

        number = tk.Label(
            row,
            text=f"{index + 1:02d}",
            bg=COLORS["surface_alt"],
            fg=COLORS["accent"],
            font=("Segoe UI", 9, "bold"),
            width=4,
            padx=6,
            pady=7,
        )
        number.grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, 12), pady=(1, 0))

        label_text = field["label"] or field["technical_name"]
        label = tk.Label(
            row,
            text=label_text,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        label.grid(row=0, column=1, sticky="ew")

        entry = tk.Entry(
            row,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        entry.grid(row=1, column=1, sticky="ew", ipady=9, pady=(6, 0))
        entry.insert(0, field["default"])

        helper_parts = []
        if field["example"]:
            helper_parts.append(f"Beispiel: {field['example']}")
        if field["hint"]:
            helper_parts.append(field["hint"])

        helper_text = " | ".join(helper_parts) if helper_parts else field["technical_name"]
        helper = tk.Label(
            row,
            text=helper_text,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=610,
        )
        helper.grid(row=2, column=1, sticky="ew", pady=(5, 0))

        entry.bind("<FocusIn>", lambda _event, item=entry: self._focus_entry(item))
        entry.bind("<FocusOut>", lambda _event, item=entry: self._blur_entry(item))
        self._bind_mousewheel(row)
        self._bind_mousewheel(entry)

        self.entries[field["technical_name"]] = entry

        if index == 0:
            entry.focus_set()

    def _focus_entry(self, entry):
        entry.configure(highlightbackground=COLORS["accent"])

    def _blur_entry(self, entry):
        entry.configure(highlightbackground=COLORS["border"])

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
            self.status_label.configure(bg="#fef3f2", fg=COLORS["danger"])
            return

        if success:
            self.status_label.configure(
                bg=COLORS["success_soft"],
                fg=COLORS["success_text"],
            )
            return

        self.status_label.configure(bg=COLORS["surface_alt"], fg=COLORS["muted"])


if __name__ == "__main__":
    app = ContractGeneratorApp()
    app.mainloop()
