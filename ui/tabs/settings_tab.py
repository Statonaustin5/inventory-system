"""
ui/tabs/settings_tab.py
-----------------------
Settings tab: configure per-product restock thresholds.
Double-click any row to update that product's threshold.
Changes take effect immediately across all tabs.
"""

from tkinter import ttk, simpledialog

from models import get_all_products, get_stock_status, update_threshold


class SettingsTab(ttk.Frame):
    def __init__(self, parent, refresh_cb):
        super().__init__(parent, padding=8)
        self.refresh_cb = refresh_cb
        self._build()

    def _build(self):
        ttk.Label(self, text="Restock thresholds",
                  font=("Helvetica", 11, "bold")).pack(anchor="w")
        ttk.Label(self,
                  text="Double-click a row to update the threshold for that product.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 8))

        cols = ("Product", "Current Stock", "Threshold", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, (280, 120, 100, 80)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w,
                             anchor="w" if col == "Product" else "center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._edit_threshold)

    def render(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        df = get_all_products()
        for _, row in df.iterrows():
            status = get_stock_status(row["qty"], row["threshold"])
            self.tree.insert("", "end", iid=str(row["id"]),
                             values=(row["name"], row["qty"], row["threshold"], status))

    def _edit_threshold(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        pid     = int(sel[0])
        current = self.tree.item(sel[0])["values"][2]
        name    = self.tree.item(sel[0])["values"][0]

        new_val = simpledialog.askinteger(
            "Update threshold",
            f"New restock threshold for\n'{name}':",
            initialvalue=current,
            minvalue=0,
            parent=self
        )
        if new_val is not None:
            update_threshold(pid, new_val)
            self.refresh_cb()
