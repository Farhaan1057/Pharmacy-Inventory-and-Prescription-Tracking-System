"""
gui/settings.py
===============
Shared UI components used across all page modules:
  Card, SectionTitle, AccentButton, DataTable, StatusBar, Sidebar
"""

import tkinter as tk
from tkinter import ttk
from database.connection import COLORS, FONTS


# ============================================================
# REUSABLE WIDGETS
# ============================================================
class Card(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                         bg=COLORS["bg_card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1, **kwargs)


class SectionTitle(tk.Label):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, text=text,
                         font=FONTS["heading"],
                         fg=COLORS["text_primary"],
                         bg=COLORS["bg_card"], **kwargs)


class AccentButton(tk.Button):
    def __init__(self, parent, text, command=None, color=None, **kwargs):
        c = color or COLORS["accent"]
        super().__init__(parent, text=text, command=command,
                         bg=c, fg=COLORS["btn_text"],
                         font=FONTS["subhead"],
                         relief="flat", bd=0,
                         padx=16, pady=8,
                         cursor="hand2",
                         activebackground=COLORS["accent_hover"],
                         activeforeground=COLORS["white"], **kwargs)
        self.bind("<Enter>", lambda e: self.configure(bg=COLORS["accent_hover"]))
        self.bind("<Leave>", lambda e: self.configure(bg=c))


class StatusBar(tk.Label):
    def __init__(self, parent):
        super().__init__(parent,
                         text="● Connected to PharmacyDB on localhost:27017",
                         font=FONTS["small"],
                         fg=COLORS["success"],
                         bg=COLORS["bg_dark"],
                         anchor="w", padx=12)


class DataTable(tk.Frame):
    """Scrollable, styled Treeview table with alternating row colours."""

    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_primary"],
                        fieldbackground=COLORS["bg_card"],
                        borderwidth=0,
                        font=FONTS["body"],
                        rowheight=28)
        style.configure("Custom.Treeview.Heading",
                        background=COLORS["accent"],
                        foreground=COLORS["white"],
                        font=FONTS["subhead"],
                        borderwidth=0,
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", COLORS["accent_light"])],
                  foreground=[("selected",  COLORS["white"])])

        self.tree = ttk.Treeview(self, columns=columns,
                                  show="headings",
                                  style="Custom.Treeview")
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(100, len(col) * 11), anchor="w")

        self.tree.tag_configure("odd",  background="#1C2128")
        self.tree.tag_configure("even", background=COLORS["bg_card"])

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert(self, values):
        tag = "odd" if len(self.tree.get_children()) % 2 else "even"
        self.tree.insert("", "end", values=values, tags=(tag,))


# ============================================================
# NAVIGATION SIDEBAR
# ============================================================
class Sidebar(tk.Frame):
    NAV_ITEMS = [
        ("OVERVIEW", [
            ("🏠", "Dashboard",      "dashboard"),
        ]),
        ("MANAGEMENT", [
            ("💊", "Medicines",      "medicines"),
            ("🏪", "Pharmacies",     "pharmacies"),
            ("👥", "Persons",        "persons"),
            ("📦", "Inventory",      "inventory"),
            ("📋", "Prescriptions",  "prescriptions"),
            ("🚚", "Supply Orders",  "orders"),
            ("🏭", "Suppliers",      "suppliers"),
        ]),
        ("ANALYTICS", [
            ("📊", "Analytics",      "analytics"),
            ("🔍", "Query Lab",      "querylab"),
        ]),
        ("DATABASE", [
            ("⚡", "Indexes",        "indexes"),
            ("🔧", "Optimization",   "optimization"),
            ("🔒", "Transactions",   "transactions"),
            ("🗄️", "Backup/Restore", "backup"),
        ]),
    ]

    def __init__(self, parent, on_navigate):
        super().__init__(parent, bg=COLORS["bg_sidebar"], width=220)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active  = None
        self._build()

    def _build(self):
        # Logo
        logo = tk.Frame(self, bg=COLORS["bg_sidebar"])
        logo.pack(fill="x", pady=(20, 0), padx=16)
        tk.Label(logo, text="💊", font=("Segoe UI", 28),
                 bg=COLORS["bg_sidebar"], fg=COLORS["accent_light"]).pack()
        tk.Label(logo, text="MedLife",
                 font=("Segoe UI", 14, "bold"),
                 fg=COLORS["text_primary"],
                 bg=COLORS["bg_sidebar"]).pack()
        tk.Label(logo, text="Pharmacy System",
                 font=FONTS["small"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_sidebar"]).pack()

        tk.Frame(self, bg=COLORS["border"], height=1).pack(
            fill="x", padx=16, pady=16)

        for section, items in self.NAV_ITEMS:
            tk.Label(self, text=section,
                     font=("Segoe UI", 8, "bold"),
                     fg=COLORS["text_muted"],
                     bg=COLORS["bg_sidebar"],
                     anchor="w").pack(fill="x", padx=20, pady=(10, 2))

            for icon, label, key in items:
                btn = tk.Button(
                    self,
                    text=f"  {icon}  {label}",
                    font=FONTS["nav"],
                    fg=COLORS["text_secondary"],
                    bg=COLORS["bg_sidebar"],
                    relief="flat", bd=0,
                    anchor="w", padx=12, pady=8,
                    cursor="hand2",
                    command=lambda k=key: self.navigate(k))
                btn.pack(fill="x", padx=8)
                btn.bind("<Enter>",
                         lambda e, b=btn: b.configure(bg=COLORS["bg_card"])
                         if b != self.buttons.get(self.active) else None)
                btn.bind("<Leave>",
                         lambda e, b=btn, k2=key:
                         b.configure(bg=COLORS["accent"]
                                     if k2 == self.active
                                     else COLORS["bg_sidebar"]))
                self.buttons[key] = btn

        tk.Label(self, text="CSC316 • Spring 2026",
                 font=FONTS["small"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_sidebar"]).pack(side="bottom", pady=12)

    def navigate(self, key):
        if self.active and self.active in self.buttons:
            self.buttons[self.active].configure(
                bg=COLORS["bg_sidebar"],
                fg=COLORS["text_secondary"])
        self.active = key
        self.buttons[key].configure(
            bg=COLORS["accent"], fg=COLORS["white"])
        self.on_navigate(key)