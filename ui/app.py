"""
ui/app.py
---------
Main application window. Owns the top bar, metric cards, alert banner,
and the tabbed notebook. Each tab is a self-contained widget imported
from ui/tabs/.
"""

import tkinter as tk
from tkinter import ttk

from models import get_all_products, get_stock_status
from ui.tabs.inventory_tab import InventoryTab
from ui.tabs.forecast_tab import ForecastTab
from ui.tabs.report_tab import ReportTab
from ui.tabs.settings_tab import SettingsTab


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Inventory Management System")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(bg="#f4f4f2")

        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    # ── Styles ─────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        BG     = "#f4f4f2"
        PANEL  = "#ffffff"
        ACCENT = "#2c3e6b"
        FG     = "#1a1a1a"
        FG2    = "#666666"

        style.configure(".",               background=BG,    foreground=FG,  font=("Helvetica", 11))
        style.configure("TFrame",          background=BG)
        style.configure("TLabel",          background=BG,    foreground=FG)
        style.configure("Sub.TLabel",      background=BG,    foreground=FG2, font=("Helvetica", 10))
        style.configure("Title.TLabel",    background=BG,    foreground=ACCENT, font=("Helvetica", 15, "bold"))
        style.configure("TButton",         background=PANEL, foreground=FG,  borderwidth=1, relief="solid", padding=(10, 5))
        style.map("TButton",               background=[("active", "#e8e8e6")])
        style.configure("Accent.TButton",  background=ACCENT, foreground="white", borderwidth=0, padding=(10, 5))
        style.map("Accent.TButton",        background=[("active", "#1a2d52")])

        style.configure("Treeview",
            background=PANEL, foreground=FG, fieldbackground=PANEL,
            rowheight=28, borderwidth=0, font=("Helvetica", 10)
        )
        style.configure("Treeview.Heading",
            background="#e8e8e6", foreground=FG2,
            font=("Helvetica", 10, "bold"), relief="flat", borderwidth=0
        )
        style.map("Treeview",
            background=[("selected", "#dce6f5")],
            foreground=[("selected", FG)]
        )

        style.configure("TNotebook",      background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",  background="#e0dfd8", foreground=FG2, padding=(14, 6))
        style.map("TNotebook.Tab",        background=[("selected", PANEL)], foreground=[("selected", FG)])
        style.configure("TEntry",         fieldbackground=PANEL, borderwidth=1, relief="solid")
        style.configure("TCombobox",      fieldbackground=PANEL, borderwidth=1, relief="solid")

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self, padding=(16, 12, 16, 8))
        top.pack(fill="x")
        ttk.Label(top, text="Inventory Management System", style="Title.TLabel").pack(side="left")
        ttk.Label(top, text="Real-time tracking · Forecasting · Alerts",
                  style="Sub.TLabel").pack(side="left", padx=(10, 0))

        # Metric cards
        self.metric_frame = ttk.Frame(self, padding=(16, 0, 16, 8))
        self.metric_frame.pack(fill="x")

        # Alert banner (hidden until needed)
        self.alert_var = tk.StringVar()
        self.alert_bar = tk.Label(
            self, textvariable=self.alert_var,
            bg="#fff3cd", fg="#856404",
            font=("Helvetica", 10), anchor="w", padx=12, pady=6
        )

        # Tabs
        self.nb = ttk.Notebook(self, padding=(16, 0, 16, 16))
        self.nb.pack(fill="both", expand=True)

        self.inv_tab  = InventoryTab(self.nb,  refresh_cb=self.refresh_all)
        self.fc_tab   = ForecastTab(self.nb)
        self.rpt_tab  = ReportTab(self.nb)
        self.cfg_tab  = SettingsTab(self.nb,   refresh_cb=self.refresh_all)

        self.nb.add(self.inv_tab,  text="  Inventory  ")
        self.nb.add(self.fc_tab,   text="  Forecast  ")
        self.nb.add(self.rpt_tab,  text="  Reports  ")
        self.nb.add(self.cfg_tab,  text="  Settings  ")

    # ── Refresh ────────────────────────────────────────────────────────────────

    def refresh_all(self):
        self._render_metrics()
        self._render_alerts()
        self.inv_tab.render()
        self.fc_tab.render()
        self.rpt_tab.render()
        self.cfg_tab.render()

    def _render_metrics(self):
        for widget in self.metric_frame.winfo_children():
            widget.destroy()

        df = get_all_products()
        if df.empty:
            return

        df["status"] = df.apply(lambda r: get_stock_status(r["qty"], r["threshold"]), axis=1)

        stats = [
            ("SKUs",            str(len(df))),
            ("Total units",     f"{int(df['qty'].sum()):,}"),
            ("Inventory value", f"${(df['qty'] * df['price']).sum():,.2f}"),
            ("Low stock",       str(int((df["status"] == "Low").sum()))),
            ("Critical",        str(int((df["status"] == "Critical").sum()))),
        ]

        for label, value in stats:
            card = tk.Frame(self.metric_frame, bg="#e8e8e6", padx=14, pady=8)
            card.pack(side="left", padx=(0, 8))
            tk.Label(card, text=label, bg="#e8e8e6", fg="#666",
                     font=("Helvetica", 9)).pack(anchor="w")
            color = (
                "#a32d2d" if label == "Critical"  and int(value) > 0 else
                "#854f0b" if label == "Low stock" and int(value) > 0 else
                "#1a1a1a"
            )
            tk.Label(card, text=value, bg="#e8e8e6", fg=color,
                     font=("Helvetica", 16, "bold")).pack(anchor="w")

    def _render_alerts(self):
        df = get_all_products()
        if df.empty:
            self.alert_bar.pack_forget()
            return

        df["status"] = df.apply(lambda r: get_stock_status(r["qty"], r["threshold"]), axis=1)
        alerts = df[df["status"] != "OK"]

        if alerts.empty:
            self.alert_bar.pack_forget()
            return

        names = ", ".join(
            f"{r['name']} ({r['qty']} units)"
            for _, r in alerts.iterrows()
        )
        self.alert_var.set(f"⚠  Restock recommended: {names}")
        self.alert_bar.pack(fill="x", before=self.nb)
