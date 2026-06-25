"""
gui/dashboard.py
================
Dashboard page — stat cards, stock-by-branch chart, alerts panel.
"""

import tkinter as tk
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.connection import COLORS, FONTS
from gui.settings import Card, SectionTitle, AccentButton


class DashboardPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self._build()

    def _build(self):
        # Destroy old children on refresh
        for w in self.winfo_children():
            w.destroy()

        # Header
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="Dashboard", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text=datetime.now().strftime("  %d %B %Y"),
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left", pady=4)
        AccentButton(hdr, "↻  Refresh", self._build).pack(side="right")

        # Stat cards
        stats_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        stats_frame.pack(fill="x", padx=24, pady=16)

        stats = self._get_stats()
        stat_defs = [
            ("💊 Medicines",      stats["medicines"],     COLORS["info"]),
            ("🏪 Pharmacies",     stats["pharmacies"],    COLORS["accent_light"]),
            ("📋 Prescriptions",  stats["prescriptions"], COLORS["success"]),
            ("📦 Inventory",      stats["inventory"],     COLORS["warning"]),
            ("🚨 Low Stock",      stats["low_stock"],     COLORS["danger"]),
            ("⚠️  Near Expiry",   stats["near_expiry"],   COLORS["warning"]),
        ]
        for i, (label, value, color) in enumerate(stat_defs):
            card = Card(stats_frame)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=str(value), font=("Segoe UI", 26, "bold"),
                     fg=color, bg=COLORS["bg_card"]).pack(pady=(16, 4))
            tk.Label(card, text=label, font=FONTS["small"],
                     fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"]).pack(pady=(0, 16))

        # Charts + alerts
        charts_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        charts_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        charts_frame.grid_columnconfigure(0, weight=3)
        charts_frame.grid_columnconfigure(1, weight=2)
        charts_frame.grid_rowconfigure(0, weight=1)

        self._stock_chart(charts_frame)
        self._alerts_panel(charts_frame)

    # ── data helpers ─────────────────────────────────────────
    def _get_stats(self):
        try:
            ninety_days = datetime.now() + timedelta(days=90)
            return {
                "medicines":     self.db.medicines.count_documents({}),
                "pharmacies":    self.db.pharmacies.count_documents({}),
                "prescriptions": self.db.prescriptions.count_documents({}),
                "inventory":     self.db.inventory.count_documents({}),
                "low_stock":     self.db.inventory.count_documents(
                    {"$expr": {"$lt": ["$currentStock", "$minimumThreshold"]}}),
                "near_expiry":   self.db.inventory.count_documents(
                    {"batches.expiryDate": {"$lte": ninety_days}}),
            }
        except Exception:
            return {k: 0 for k in
                    ["medicines", "pharmacies", "prescriptions",
                     "inventory", "low_stock", "near_expiry"]}

    def _stock_chart(self, parent):
        card = Card(parent)
        card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        SectionTitle(card, "📊  Stock Level by Branch").pack(
            anchor="w", padx=16, pady=(14, 8))
        try:
            pipeline = [
                {"$lookup": {"from": "pharmacies", "localField": "pharmacyId",
                             "foreignField": "_id", "as": "pha"}},
                {"$group": {
                    "_id":   {"$arrayElemAt": ["$pha.name", 0]},
                    "total": {"$sum": "$currentStock"},
                    "low":   {"$sum": {"$cond": [
                        {"$lt": ["$currentStock", "$minimumThreshold"]}, 1, 0]}}
                }},
                {"$sort": {"total": -1}}
            ]
            data = list(self.db.inventory.aggregate(pipeline))
            if not data:
                tk.Label(card, text="No inventory data",
                         fg=COLORS["text_muted"], bg=COLORS["bg_card"],
                         font=FONTS["body"]).pack(expand=True)
                return

            names  = [d["_id"].split("—")[-1].strip()
                      if d["_id"] else "Unknown" for d in data]
            totals = [d["total"] for d in data]
            lows   = [d["low"]   for d in data]

            fig, ax = plt.subplots(figsize=(6, 3.2), facecolor=COLORS["bg_card"])
            ax.set_facecolor(COLORS["bg_card"])
            x = range(len(names))
            ax.bar([i - 0.2 for i in x], totals, 0.4,
                   color=COLORS["accent_light"], label="Total Stock", zorder=3)
            ax.bar([i + 0.2 for i in x], lows, 0.4,
                   color=COLORS["danger"], label="Low Stock Items", zorder=3)
            ax.set_xticks(list(x))
            ax.set_xticklabels(names, rotation=30, ha="right",
                               color=COLORS["text_secondary"], fontsize=8)
            ax.tick_params(colors=COLORS["text_secondary"])
            ax.spines[:].set_color(COLORS["border"])
            ax.set_ylabel("Units", color=COLORS["text_secondary"], fontsize=9)
            ax.legend(fontsize=8, labelcolor=COLORS["text_secondary"],
                      facecolor=COLORS["bg_card"],
                      edgecolor=COLORS["border"])
            ax.grid(axis="y", color=COLORS["border"],
                    linestyle="--", alpha=0.5, zorder=0)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True,
                                        padx=8, pady=(0, 12))
            plt.close(fig)
        except Exception as e:
            tk.Label(card, text=f"Chart error: {e}",
                     fg=COLORS["danger"], bg=COLORS["bg_card"],
                     font=FONTS["small"]).pack(padx=12, pady=8)

    def _alerts_panel(self, parent):
        card = Card(parent)
        card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        SectionTitle(card, "🚨  Active Alerts").pack(
            anchor="w", padx=16, pady=(14, 8))
        try:
            low = list(self.db.inventory.aggregate([
                {"$match": {"$expr": {"$lt": ["$currentStock",
                                              "$minimumThreshold"]}}},
                {"$lookup": {"from": "medicines", "localField": "medicineId",
                             "foreignField": "_id", "as": "med"}},
                {"$lookup": {"from": "pharmacies", "localField": "pharmacyId",
                             "foreignField": "_id", "as": "pha"}},
                {"$project": {
                    "med": {"$arrayElemAt": ["$med.name", 0]},
                    "pha": {"$arrayElemAt": ["$pha.name", 0]},
                    "currentStock": 1, "minimumThreshold": 1
                }},
                {"$limit": 8}
            ]))

            ninety = datetime.now() + timedelta(days=90)
            near_exp = list(self.db.inventory.aggregate([
                {"$unwind": "$batches"},
                {"$match": {"batches.expiryDate": {"$lte": ninety}}},
                {"$lookup": {"from": "medicines", "localField": "medicineId",
                             "foreignField": "_id", "as": "med"}},
                {"$project": {
                    "med":    {"$arrayElemAt": ["$med.name", 0]},
                    "expiry": "$batches.expiryDate",
                    "qty":    "$batches.quantityRemaining"
                }},
                {"$limit": 5}
            ]))

            sf = tk.Frame(card, bg=COLORS["bg_card"])
            sf.pack(fill="both", expand=True, padx=12, pady=(0, 12))

            if low:
                tk.Label(sf, text="Low Stock", font=FONTS["subhead"],
                         fg=COLORS["danger"],
                         bg=COLORS["bg_card"]).pack(anchor="w", pady=(4, 2))
                for item in low:
                    name = (item.get("med") or "Unknown")[:22]
                    stk  = item.get("currentStock", 0)
                    thr  = item.get("minimumThreshold", 0)
                    row  = tk.Frame(sf, bg="#2D1515", pady=3)
                    row.pack(fill="x", pady=1)
                    tk.Label(row, text=f"⚠ {name}", font=FONTS["small"],
                             fg=COLORS["danger"], bg="#2D1515",
                             anchor="w").pack(side="left", padx=6)
                    tk.Label(row, text=f"{stk}/{thr}", font=FONTS["small"],
                             fg=COLORS["warning"],
                             bg="#2D1515").pack(side="right", padx=6)

            if near_exp:
                tk.Label(sf, text="Near Expiry (90 days)", font=FONTS["subhead"],
                         fg=COLORS["warning"],
                         bg=COLORS["bg_card"]).pack(anchor="w", pady=(10, 2))
                for item in near_exp:
                    name   = (item.get("med") or "Unknown")[:22]
                    expdt  = item.get("expiry")
                    expstr = expdt.strftime("%d %b %Y") if expdt else "?"
                    row    = tk.Frame(sf, bg="#2D2500", pady=3)
                    row.pack(fill="x", pady=1)
                    tk.Label(row, text=f"⏰ {name}", font=FONTS["small"],
                             fg=COLORS["warning"], bg="#2D2500",
                             anchor="w").pack(side="left", padx=6)
                    tk.Label(row, text=expstr, font=FONTS["small"],
                             fg=COLORS["text_secondary"],
                             bg="#2D2500").pack(side="right", padx=6)

            if not low and not near_exp:
                tk.Label(sf, text="✅  No active alerts", font=FONTS["body"],
                         fg=COLORS["success"],
                         bg=COLORS["bg_card"]).pack(pady=20)
        except Exception as e:
            tk.Label(card, text=f"Error: {e}", fg=COLORS["danger"],
                     bg=COLORS["bg_card"],
                     font=FONTS["small"]).pack(padx=12, pady=8)