"""
ui/tabs/inventory_tab.py
------------------------
Inventory tab: searchable/filterable product table with add, edit,
and delete actions.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from models import get_all_products, get_product, add_product, update_product, delete_product, get_stock_status
from ui.dialogs import ItemDialog


class InventoryTab(ttk.Frame):
    def __init__(self, parent, refresh_cb):
        super().__init__(parent)
        self.refresh_cb = refresh_cb
        self._build()

    def _build(self):
        # Filter row
        frow = ttk.Frame(self, padding=(0, 8, 0, 8))
        frow.pack(fill="x")

        ttk.Label(frow, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.render())
        ttk.Entry(frow, textvariable=self.search_var, width=22).pack(side="left", padx=(4, 12))

        ttk.Label(frow, text="Category:").pack(side="left")
        self.cat_var = tk.StringVar(value="All")
        self.cat_combo = ttk.Combobox(frow, textvariable=self.cat_var, width=14, state="readonly")
        self.cat_combo.pack(side="left", padx=(4, 12))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda _: self.render())

        ttk.Label(frow, text="Status:").pack(side="left")
        self.status_var = tk.StringVar(value="All")
        ttk.Combobox(frow, textvariable=self.status_var,
                     values=["All", "OK", "Low", "Critical"],
                     width=10, state="readonly").pack(side="left", padx=4)
        self.status_var.trace_add("write", lambda *_: self.render())

        ttk.Button(frow, text="＋ Add item",
                   style="Accent.TButton",
                   command=self._open_add).pack(side="right")

        # Treeview
        cols = ("Name", "Category", "Stock", "Threshold", "Price", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        widths = (240, 110, 70, 90, 80, 80)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w,
                             anchor="w" if col in ("Name", "Category") else "center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Action buttons
        btn_row = ttk.Frame(self, padding=(0, 8, 0, 0))
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="✏  Edit selected",   command=self._open_edit).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="🗑  Delete selected", command=self._delete).pack(side="left")

    # ── Render ─────────────────────────────────────────────────────────────────

    def render(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        df = get_all_products()
        if df.empty:
            return

        # Refresh category dropdown
        cats = ["All"] + sorted(df["category"].unique().tolist())
        prev = self.cat_var.get()
        self.cat_combo["values"] = cats
        if prev not in cats:
            self.cat_var.set("All")

        q    = self.search_var.get().lower()
        cat  = self.cat_var.get()
        stat = self.status_var.get()

        df["status"] = df.apply(lambda r: get_stock_status(r["qty"], r["threshold"]), axis=1)

        if q:
            mask = (df["name"].str.lower().str.contains(q) |
                    df["category"].str.lower().str.contains(q))
            df = df[mask]
        if cat != "All":
            df = df[df["category"] == cat]
        if stat != "All":
            df = df[df["status"] == stat]

        for _, row in df.iterrows():
            self.tree.insert("", "end", iid=str(row["id"]), values=(
                row["name"], row["category"], row["qty"],
                row["threshold"], f"${row['price']:.2f}", row["status"]
            ))

    # ── Actions ────────────────────────────────────────────────────────────────

    def _open_add(self):
        ItemDialog(self, title="Add item", on_save=self._save_new)

    def _open_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a row to edit.")
            return
        pid  = int(sel[0])
        data = get_product(pid)
        if data:
            ItemDialog(self, title="Edit item", data=data,
                       on_save=lambda d: self._save_edit(pid, d))

    def _save_new(self, data: dict):
        add_product(data)
        self.refresh_cb()

    def _save_edit(self, pid: int, data: dict):
        update_product(pid, data)
        self.refresh_cb()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a row to delete.")
            return
        pid  = int(sel[0])
        name = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm delete", f"Delete '{name}'? This cannot be undone."):
            delete_product(pid)
            self.refresh_cb()
