"""
ui/tabs/forecast_tab.py
-----------------------
Forecast tab: shows OLS linear regression results for each product —
slope (β₁), intercept (β₀), R², predicted next-period demand, and trend.
"""

from tkinter import ttk

from models import get_all_products, get_sales
from forecasting import linear_regression_forecast


class ForecastTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=8)
        self._build()

    def _build(self):
        ttk.Label(self, text="Demand forecast — OLS linear regression (ŷ = β₀ + β₁x)",
                  font=("Helvetica", 11, "bold")).pack(anchor="w")
        ttk.Label(self,
                  text="Predicted next-period units based on 8-week sales history.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 8))

        cols = ("Product", "8-wk Avg", "β₀", "β₁ Slope", "R²", "Next Est.", "Trend")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="none")
        widths = (220, 80, 80, 90, 70, 90, 120)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w,
                             anchor="w" if col == "Product" else "center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def render(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        df = get_all_products()
        for _, row in df.iterrows():
            sales = get_sales(row["id"])
            if len(sales) < 2:
                continue
            result = linear_regression_forecast(sales, len(sales) + 1)
            avg    = round(sum(sales) / len(sales), 1)
            self.tree.insert("", "end", values=(
                row["name"], avg,
                result["b0"], result["b1"], result["r2"],
                result["predicted"], result["trend"]
            ))
