"""
ui/dialogs.py
-------------
Modal dialog for adding and editing inventory items.
Accepts an optional `data` dict to pre-fill fields when editing.
Calls `on_save(data)` with validated field values on confirm.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class ItemDialog(tk.Toplevel):
    FIELDS = [
        ("Product name",      "name",      str,   ""),
        ("Category",          "category",  str,   ""),
        ("Current stock",     "qty",       int,   0),
        ("Restock threshold", "threshold", int,   10),
        ("Unit price ($)",    "price",     float, 0.0),
    ]

    def __init__(self, parent, title: str, on_save, data: dict = None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.on_save = on_save

        self._build(data or {})
        self.transient(parent)
        self.focus()

    def _build(self, data: dict):
        pad = {"padx": 12, "pady": 5}
        self.vars: dict[str, tuple[tk.StringVar, type]] = {}

        for i, (label, key, typ, default) in enumerate(self.FIELDS):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky="w", **pad)
            var = tk.StringVar(value=str(data.get(key, default)))
            self.vars[key] = (var, typ)
            ttk.Entry(self, textvariable=var, width=28).grid(row=i, column=1, **pad)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(self.FIELDS), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Save", command=self._submit,
                   style="Accent.TButton").pack(side="left")

    def _submit(self):
        result = {}
        for key, (var, typ) in self.vars.items():
            raw = var.get().strip()
            if not raw:
                messagebox.showerror("Validation error",
                                     f"'{key}' cannot be empty.", parent=self)
                return
            try:
                result[key] = typ(raw)
            except ValueError:
                messagebox.showerror("Validation error",
                                     f"'{key}' must be a valid {typ.__name__}.", parent=self)
                return

        self.on_save(result)
        self.destroy()
