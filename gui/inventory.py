"""
gui/inventory.py
================
Pages: MedicinesPage, InventoryPage, GenericPage
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database.connection import COLORS, FONTS
from gui.settings import Card, AccentButton, DataTable


# ============================================================
# PAGE: MEDICINES
# ============================================================
class MedicinesPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db        = db
        self.page_num  = 0
        self.page_size = 15
        self.filter_type = tk.StringVar(value="All")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="💊  Medicines Registry", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "+ Add Medicine", self._add_dialog).pack(side="right")

        fb = tk.Frame(self, bg=COLORS["bg_dark"])
        fb.pack(fill="x", padx=24, pady=12)
        tk.Label(fb, text="Search:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        self.search_var = tk.StringVar()
        se = tk.Entry(fb, textvariable=self.search_var,
                      font=FONTS["body"], bg=COLORS["bg_card"],
                      fg=COLORS["text_primary"],
                      insertbackground=COLORS["text_primary"],
                      relief="flat", bd=1, width=28)
        se.pack(side="left", padx=(6, 16), ipady=5)
        se.bind("<Return>", lambda e: self._load_data())

        tk.Label(fb, text="Type:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        cb = ttk.Combobox(fb, textvariable=self.filter_type,
                          values=["All", "PrescriptionMedicine", "OTCMedicine"],
                          width=20, state="readonly", font=FONTS["body"])
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self._load_data())
        AccentButton(fb, "🔍 Search", self._load_data,
                     color=COLORS["info"]).pack(side="left", padx=8)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols = ["Name", "Generic Name", "Type", "Category",
                "Price (Rs)", "Min Stock", "Controlled", "Requires Rx"]
        self.table = DataTable(card, cols)
        self.table.pack(fill="both", expand=True, padx=8, pady=8)

        pag = tk.Frame(self, bg=COLORS["bg_dark"])
        pag.pack(fill="x", padx=24, pady=(0, 12))
        AccentButton(pag, "◀ Prev", self._prev_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self.page_label = tk.Label(pag, text="Page 1", font=FONTS["body"],
                                   fg=COLORS["text_secondary"], bg=COLORS["bg_dark"])
        self.page_label.pack(side="left", padx=8)
        AccentButton(pag, "Next ▶", self._next_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self._load_data()

    def _load_data(self):
        self.table.clear()
        try:
            query = {}
            s = self.search_var.get().strip()
            if s:
                query["$or"] = [
                    {"name":        {"$regex": s, "$options": "i"}},
                    {"genericName": {"$regex": s, "$options": "i"}}
                ]
            t = self.filter_type.get()
            if t != "All":
                query["type"] = t
            skip = self.page_num * self.page_size
            meds = list(self.db.medicines.find(query)
                        .skip(skip).limit(self.page_size))
            cat_map = {c["_id"]: c["name"]
                       for c in self.db.categories.find({})}
            for m in meds:
                self.table.insert([
                    m.get("name", "—"),
                    m.get("genericName", "—"),
                    m.get("type", "—"),
                    cat_map.get(m.get("categoryId"), "—"),
                    f"{m.get('unitPrice', 0):.2f}",
                    m.get("minimumStockThreshold", "—"),
                    "Yes" if m.get("controlledSubstance") else "No",
                    "Yes" if m.get("requiresPrescription") else "No",
                ])
            total = self.db.medicines.count_documents(query)
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1; self._load_data()

    def _next_page(self):
        self.page_num += 1; self._load_data()

    def _add_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add New Medicine")
        dlg.configure(bg=COLORS["bg_card"])
        dlg.geometry("500x520")
        dlg.grab_set()
        tk.Label(dlg, text="Add New Medicine", font=FONTS["heading"],
                 fg=COLORS["text_primary"],
                 bg=COLORS["bg_card"]).pack(pady=(20, 16))
        fields = {}
        field_defs = [
            ("Medicine Name",      "name"),
            ("Generic Name",       "genericName"),
            ("Manufacturer",       "manufacturer"),
            ("Unit Price (Rs)",    "unitPrice"),
            ("Min Stock Threshold","minimumStockThreshold"),
            ("Strength",           "strength"),
        ]
        form = tk.Frame(dlg, bg=COLORS["bg_card"])
        form.pack(fill="x", padx=24)
        for label, key in field_defs:
            tk.Label(form, text=label, font=FONTS["body"],
                     fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"]).pack(anchor="w", pady=(6, 0))
            e = tk.Entry(form, font=FONTS["body"], bg=COLORS["bg_dark"],
                         fg=COLORS["text_primary"],
                         insertbackground=COLORS["text_primary"],
                         relief="flat", bd=1)
            e.pack(fill="x", ipady=5)
            fields[key] = e
        tk.Label(form, text="Type", font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(6, 0))
        type_var = tk.StringVar(value="PrescriptionMedicine")
        ttk.Combobox(form, textvariable=type_var,
                     values=["PrescriptionMedicine", "OTCMedicine"],
                     state="readonly",
                     font=FONTS["body"]).pack(fill="x")

        def save():
            try:
                doc = {
                    "name":                  fields["name"].get(),
                    "genericName":           fields["genericName"].get(),
                    "manufacturer":          fields["manufacturer"].get(),
                    "type":                  type_var.get(),
                    "unitPrice":             float(fields["unitPrice"].get() or 0),
                    "minimumStockThreshold": int(fields["minimumStockThreshold"].get() or 0),
                    "strength":              fields["strength"].get(),
                    "requiresPrescription":  type_var.get() == "PrescriptionMedicine",
                    "controlledSubstance":   False,
                }
                self.db.medicines.insert_one(doc)
                messagebox.showinfo("Success",
                    f"Medicine '{doc['name']}' added successfully!")
                dlg.destroy()
                self._load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        AccentButton(dlg, "💾  Save Medicine", save).pack(pady=20)


# ============================================================
# PAGE: INVENTORY
# ============================================================
class InventoryPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db          = db
        self.page_num    = 0
        self.page_size   = 15
        self.filter_alert = tk.StringVar(value="All")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="📦  Inventory Management", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._load_data).pack(side="right")

        fb = tk.Frame(self, bg=COLORS["bg_dark"])
        fb.pack(fill="x", padx=24, pady=12)
        tk.Label(fb, text="Show:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        ttk.Combobox(fb, textvariable=self.filter_alert,
                     values=["All", "Low Stock Only", "Near Expiry"],
                     width=18, state="readonly",
                     font=FONTS["body"]).pack(side="left", padx=6)
        AccentButton(fb, "Apply", self._load_data,
                     color=COLORS["info"]).pack(side="left", padx=6)

        tk.Label(fb, text="    Adjust Stock →", font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(16, 4))
        self.adj_med = tk.Entry(fb, font=FONTS["body"], bg=COLORS["bg_card"],
                                fg=COLORS["text_primary"],
                                insertbackground=COLORS["text_primary"],
                                relief="flat", width=24, bd=1)
        self.adj_med.insert(0, "Medicine Name")
        self.adj_med.pack(side="left", padx=4, ipady=4)
        self.adj_qty = tk.Entry(fb, font=FONTS["body"], bg=COLORS["bg_card"],
                                fg=COLORS["text_primary"],
                                insertbackground=COLORS["text_primary"],
                                relief="flat", width=8, bd=1)
        self.adj_qty.insert(0, "±Qty")
        self.adj_qty.pack(side="left", padx=4, ipady=4)
        AccentButton(fb, "Update", self._update_stock,
                     color=COLORS["warning"]).pack(side="left", padx=4)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols = ["Medicine", "Pharmacy", "City", "Current Stock",
                "Min Threshold", "Shortfall", "Batch", "Expiry", "Status"]
        self.table = DataTable(card, cols)
        self.table.pack(fill="both", expand=True, padx=8, pady=8)

        pag = tk.Frame(self, bg=COLORS["bg_dark"])
        pag.pack(fill="x", padx=24, pady=(0, 12))
        AccentButton(pag, "◀ Prev", self._prev_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self.page_label = tk.Label(pag, text="Page 1", font=FONTS["body"],
                                   fg=COLORS["text_secondary"], bg=COLORS["bg_dark"])
        self.page_label.pack(side="left", padx=8)
        AccentButton(pag, "Next ▶", self._next_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self._load_data()

    def _load_data(self):
        self.table.clear()
        try:
            pipeline = [
                {"$lookup": {"from": "medicines", "localField": "medicineId",
                             "foreignField": "_id", "as": "med"}},
                {"$lookup": {"from": "pharmacies", "localField": "pharmacyId",
                             "foreignField": "_id", "as": "pha"}},
                {"$unwind": {"path": "$batches",
                             "preserveNullAndEmptyArrays": True}},
            ]
            fa = self.filter_alert.get()
            if fa == "Low Stock Only":
                pipeline.append({"$match": {
                    "$expr": {"$lt": ["$currentStock", "$minimumThreshold"]}}})
            elif fa == "Near Expiry":
                ninety = datetime.now() + timedelta(days=90)
                pipeline.append({"$match": {
                    "batches.expiryDate": {"$lte": ninety}}})
            pipeline += [{"$skip": self.page_num * self.page_size},
                         {"$limit": self.page_size}]

            rows = list(self.db.inventory.aggregate(pipeline))
            now  = datetime.now()
            for r in rows:
                med   = (r.get("med") or [{}]); med = med[0] if med else {}
                pha   = (r.get("pha") or [{}]); pha = pha[0] if pha else {}
                batch = r.get("batches") or {}
                cur   = r.get("currentStock", 0)
                thr   = r.get("minimumThreshold", 0)
                short = max(0, thr - cur)
                exp   = batch.get("expiryDate")
                exp_s = exp.strftime("%d %b %Y") if exp else "—"
                if cur < thr:
                    status = "🔴 LOW STOCK"
                elif exp and exp <= now + timedelta(days=90):
                    status = "🟡 NEAR EXPIRY"
                else:
                    status = "🟢 OK"
                self.table.insert([
                    med.get("name", "—")[:30],
                    (pha.get("name") or "—").split("—")[-1].strip()[:20],
                    pha.get("city", "—"),
                    cur, thr, short,
                    batch.get("batchNumber", "—")[:16],
                    exp_s, status
                ])
            self.page_label.config(
                text=f"Page {self.page_num+1}  ({len(rows)} records shown)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_stock(self):
        med_name = self.adj_med.get().strip()
        try:
            qty = int(self.adj_qty.get().strip())
        except Exception:
            messagebox.showerror("Error",
                "Enter a valid integer quantity (e.g. -14 or +50)"); return
        try:
            med = self.db.medicines.find_one(
                {"name": {"$regex": med_name, "$options": "i"}})
            if not med:
                messagebox.showerror("Error",
                    f"Medicine '{med_name}' not found"); return
            res = self.db.inventory.update_many(
                {"medicineId": med["_id"]},
                {"$inc": {"currentStock": qty}})
            messagebox.showinfo("Updated",
                f"Stock adjusted by {qty} for {res.modified_count} record(s).")
            self._load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1; self._load_data()

    def _next_page(self):
        self.page_num += 1; self._load_data()


# ============================================================
# PAGE: GENERIC TABLE PAGE (Pharmacies, Persons, Suppliers, Orders)
# ============================================================
class GenericPage(tk.Frame):
    def __init__(self, parent, db, title, collection,
                 columns, extractor, page_size=15):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db         = db
        self.collection = db[collection]
        self.title_text = title
        self.columns    = columns
        self.extractor  = extractor
        self.page_num   = 0
        self.page_size  = page_size
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text=self.title_text, font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._load_data).pack(side="right")

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=16)
        self.table = DataTable(card, self.columns)
        self.table.pack(fill="both", expand=True, padx=8, pady=8)

        pag = tk.Frame(self, bg=COLORS["bg_dark"])
        pag.pack(fill="x", padx=24, pady=(0, 12))
        AccentButton(pag, "◀ Prev", self._prev_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self.page_label = tk.Label(pag, text="Page 1", font=FONTS["body"],
                                   fg=COLORS["text_secondary"], bg=COLORS["bg_dark"])
        self.page_label.pack(side="left", padx=8)
        AccentButton(pag, "Next ▶", self._next_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self._load_data()

    def _load_data(self):
        self.table.clear()
        try:
            skip  = self.page_num * self.page_size
            docs  = list(self.collection.find({}).skip(skip).limit(self.page_size))
            total = self.collection.count_documents({})
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            for doc in docs:
                self.table.insert(self.extractor(doc))
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1; self._load_data()

    def _next_page(self):
        self.page_num += 1; self._load_data()
    
            