"""
ui/tabs/report_tab.py
---------------------
Reports tab: weekly performance summary including WoW % change,
revenue per product, next-period forecast, and stock status.
"""

import tkinter as tk
from tkinter import ttk

from models import get_all_products, get_sales, get_stock_status
from forecasting import linear_regression_forecast


class ReportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=8)
        self._build()

    def _build(self):
        ttk.Label(self, text="Weekly performance report",
                  font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 4))

        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill="x", pady=(0, 8))

        cols = ("Product", "Category", "Last Wk Sales", "WoW %",
                "Revenue", "Next Est.", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="none")
        widths = (200, 110, 110, 80, 100, 90, 80)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w,
                             anchor="w" if col in ("Product", "Category") else "center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def render(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        df = get_all_products()
        if df.empty:
            return

        total_rev   = 0.0
        total_units = 0

        for _, row in df.iterrows():
            sales = get_sales(row["id"])
            if len(sales) < 2:
                continue

            last, prev = sales[-1], sales[-2]
            wow    = round((last - prev) / prev * 100, 1) if prev else 0.0
            rev    = round(last * row["price"], 2)
            result = linear_regression_forecast(sales, len(sales) + 1)
            status = get_stock_status(row["qty"], row["threshold"])

            total_rev   += rev
            total_units += last

            self.tree.insert("", "end", values=(
                row["name"], row["category"], last,
                f"{'+' if wow >= 0 else ''}{wow}%",
                f"${rev:,.2f}", result["predicted"], status
            ))

        # Summary metric cards
        avg_unit = round(total_rev / total_units, 2) if total_units else 0
        for label, val in [
            ("Weekly revenue", f"${total_rev:,.2f}"),
            ("Units sold",     str(total_units)),
            ("Avg unit value", f"${avg_unit}"),
        ]:
            card = tk.Frame(self.summary_frame, bg="#e8e8e6", padx=14, pady=8)
            card.pack(side="left", padx=(0, 8))
            tk.Label(card, text=label, bg="#e8e8e6", fg="#666",
                     font=("Helvetica", 9)).pack(anchor="w")
            tk.Label(card, text=val, bg="#e8e8e6", fg="#1a1a1a",
                     font=("Helvetica", 15, "bold")).pack(anchor="w")
