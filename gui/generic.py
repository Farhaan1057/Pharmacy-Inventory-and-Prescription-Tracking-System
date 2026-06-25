"""
gui/generic.py
==============
Generic pages for displaying tabular data:
  PrescriptionsPage, PharmaciesPage, PersonsPage, SuppliersPage, OrdersPage,
  AnalyticsPage, QueryLabPage, IndexesPage, OptimizationPage, BackupRestorePage,
  TransactionPrescriptionPage
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.connection import COLORS, FONTS, DatabaseConnection
from gui.settings import Card, AccentButton, DataTable, SectionTitle


# ============================================================
# PAGE: PRESCRIPTIONS
# ============================================================
class PrescriptionsPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self.page_num = 0
        self.page_size = 15
        self.status_filter = tk.StringVar(value="All")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="📋  Prescriptions Management", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "+ New Rx", self._add_rx_dialog).pack(side="right")

        fb = tk.Frame(self, bg=COLORS["bg_dark"])
        fb.pack(fill="x", padx=24, pady=12)
        
        tk.Label(fb, text="Status:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        ttk.Combobox(fb, textvariable=self.status_filter,
                     values=["All", "Pending", "Dispensed", "Expired", "Cancelled"],
                     width=18, state="readonly",
                     font=FONTS["body"]).pack(side="left", padx=6)
        AccentButton(fb, "Apply", self._load_data,
                     color=COLORS["info"]).pack(side="left", padx=6)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols = ["Rx Date", "Patient", "Doctor", "Medicine", "Qty", "Status", "Pharmacy", "Dispensed"]
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
            if self.status_filter.get() != "All":
                query["status"] = self.status_filter.get()
            
            skip = self.page_num * self.page_size
            rxs = list(self.db.prescriptions.find(query)
                       .sort("prescriptionDate", -1)
                       .skip(skip).limit(self.page_size))
            
            for rx in rxs:
                patient = self.db.persons.find_one({"_id": rx.get("patientId")}) or {}
                doctor = self.db.persons.find_one({"_id": rx.get("doctorId")}) or {}
                med = self.db.medicines.find_one({"_id": rx.get("medicineId")}) or {}
                pha = self.db.pharmacies.find_one({"_id": rx.get("pharmacyId")}) or {}
                
                self.table.insert([
                    rx.get("prescriptionDate", datetime.now()).strftime("%d-%b-%y"),
                    patient.get("name", "—")[:20],
                    doctor.get("name", "—")[:20],
                    med.get("name", "—")[:15],
                    rx.get("quantityPrescribed", "—"),
                    rx.get("status", "Pending"),
                    pha.get("name", "—").split("—")[-1].strip()[:15],
                    rx.get("dispensedAt", "—"),
                ])
            
            total = self.db.prescriptions.count_documents(query)
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self._load_data()

    def _next_page(self):
        self.page_num += 1
        self._load_data()

    def _add_rx_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("New Prescription")
        dlg.configure(bg=COLORS["bg_card"])
        dlg.geometry("500x450")
        dlg.grab_set()
        
        SectionTitle(dlg, "New Prescription").pack(pady=(20, 16), padx=20)
        
        form = tk.Frame(dlg, bg=COLORS["bg_card"])
        form.pack(fill="x", padx=24, expand=True)
        
        # Patient
        tk.Label(form, text="Patient *", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        patients = [p["name"] for p in self.db.persons.find({"roles": "Patient"})]
        patient_var = tk.StringVar(value=patients[0] if patients else "")
        ttk.Combobox(form, textvariable=patient_var,
                     values=patients, state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        # Doctor
        tk.Label(form, text="Doctor *", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        doctors = [p["name"] for p in self.db.persons.find({"roles": "Doctor"})]
        doctor_var = tk.StringVar(value=doctors[0] if doctors else "")
        ttk.Combobox(form, textvariable=doctor_var,
                     values=doctors, state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        # Medicine
        tk.Label(form, text="Medicine *", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        meds = [m["name"] for m in self.db.medicines.find({})]
        med_var = tk.StringVar(value=meds[0] if meds else "")
        ttk.Combobox(form, textvariable=med_var,
                     values=meds, state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        # Quantity
        tk.Label(form, text="Quantity *", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        qty_e = tk.Entry(form, font=FONTS["body"], bg=COLORS["bg_dark"],
                         fg=COLORS["text_primary"],
                         insertbackground=COLORS["text_primary"],
                         relief="flat", bd=1)
        qty_e.pack(fill="x", ipady=6)
        
        # Pharmacy
        tk.Label(form, text="Pharmacy *", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        pharmacies = [p["name"] for p in self.db.pharmacies.find({})]
        pha_var = tk.StringVar(value=pharmacies[0] if pharmacies else "")
        ttk.Combobox(form, textvariable=pha_var,
                     values=pharmacies, state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        def save():
            try:
                patient = self.db.persons.find_one({"name": patient_var.get(), "roles": "Patient"})
                doctor = self.db.persons.find_one({"name": doctor_var.get(), "roles": "Doctor"})
                med = self.db.medicines.find_one({"name": med_var.get()})
                pha = self.db.pharmacies.find_one({"name": pha_var.get()})
                
                if not all([patient, doctor, med, pha]):
                    messagebox.showerror("Error", "Invalid selection.")
                    return
                
                doc = {
                    "patientId": patient["_id"],
                    "doctorId": doctor["_id"],
                    "medicineId": med["_id"],
                    "pharmacyId": pha["_id"],
                    "prescriptionDate": datetime.now(),
                    "quantityPrescribed": int(qty_e.get() or 1),
                    "status": "Pending",
                    "isControlledSubstance": med.get("controlledSubstance", False),
                }
                
                self.db.prescriptions.insert_one(doc)
                messagebox.showinfo("Success", "Prescription created successfully!")
                dlg.destroy()
                self._load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        AccentButton(dlg, "💾  Create Prescription", save).pack(pady=20)


# ============================================================
# PAGE: PHARMACIES
# ============================================================
class PharmaciesPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self.page_num = 0
        self.page_size = 15
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🏪  Pharmacies", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._load_data).pack(side="right")

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=16)
        cols = ["Name", "Address", "City", "Phone", "Email", "License"]
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
            skip = self.page_num * self.page_size
            pharmacies = list(self.db.pharmacies.find({})
                             .skip(skip).limit(self.page_size))
            
            for p in pharmacies:
                self.table.insert([
                    p.get("name", "—")[:25],
                    p.get("address", "—")[:25],
                    p.get("city", "—"),
                    p.get("phone", "—"),
                    p.get("email", "—")[:20],
                    p.get("licenseNumber", "—")[:15],
                ])
            
            total = self.db.pharmacies.count_documents({})
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self._load_data()

    def _next_page(self):
        self.page_num += 1
        self._load_data()


# ============================================================
# PAGE: PERSONS
# ============================================================
class PersonsPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self.page_num = 0
        self.page_size = 15
        self.role_filter = tk.StringVar(value="All")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="👥  Persons Database", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._load_data).pack(side="right")

        fb = tk.Frame(self, bg=COLORS["bg_dark"])
        fb.pack(fill="x", padx=24, pady=12)
        
        tk.Label(fb, text="Role:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        ttk.Combobox(fb, textvariable=self.role_filter,
                     values=["All", "Patient", "Doctor", "Pharmacist", "Manager"],
                     width=18, state="readonly", font=FONTS["body"]).pack(side="left", padx=6)
        AccentButton(fb, "Apply", self._load_data,
                     color=COLORS["info"]).pack(side="left", padx=6)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols = ["Name", "Role", "Contact", "Email", "Address", "City"]
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
            if self.role_filter.get() != "All":
                query["roles"] = self.role_filter.get()
            
            skip = self.page_num * self.page_size
            persons = list(self.db.persons.find(query)
                          .skip(skip).limit(self.page_size))
            
            for p in persons:
                self.table.insert([
                    p.get("name", "—")[:25],
                    ", ".join(p.get("roles", []))[:20],
                    p.get("contactNumber", "—"),
                    p.get("email", "—")[:20],
                    p.get("address", "—")[:20],
                    p.get("city", "—"),
                ])
            
            total = self.db.persons.count_documents(query)
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self._load_data()

    def _next_page(self):
        self.page_num += 1
        self._load_data()


# ============================================================
# PAGE: SUPPLIERS
# ============================================================
class SuppliersPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self.page_num = 0
        self.page_size = 15
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🏭  Suppliers", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._load_data).pack(side="right")

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=16)
        cols = ["Company Name", "Contact Person", "Phone", "Email", "Address", "Rating"]
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
            skip = self.page_num * self.page_size
            suppliers = list(self.db.suppliers.find({})
                            .skip(skip).limit(self.page_size))
            
            for s in suppliers:
                rating = s.get("rating", 0)
                rating_str = "⭐" * int(rating) if rating else "—"
                self.table.insert([
                    s.get("companyName", "—")[:25],
                    s.get("contactPerson", "—")[:20],
                    s.get("phone", "—"),
                    s.get("email", "—")[:20],
                    s.get("address", "—")[:25],
                    rating_str,
                ])
            
            total = self.db.suppliers.count_documents({})
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self._load_data()

    def _next_page(self):
        self.page_num += 1
        self._load_data()


# ============================================================
# PAGE: SUPPLY ORDERS
# ============================================================
class OrdersPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self.page_num = 0
        self.page_size = 15
        self.status_filter = tk.StringVar(value="All")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🚚  Supply Orders", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._load_data).pack(side="right")

        fb = tk.Frame(self, bg=COLORS["bg_dark"])
        fb.pack(fill="x", padx=24, pady=12)
        
        tk.Label(fb, text="Status:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        ttk.Combobox(fb, textvariable=self.status_filter,
                     values=["All", "Pending", "Delivered", "Cancelled"],
                     width=18, state="readonly", font=FONTS["body"]).pack(side="left", padx=6)
        AccentButton(fb, "Apply", self._load_data,
                     color=COLORS["info"]).pack(side="left", padx=6)

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols = ["Order ID", "Supplier", "Pharmacy", "Medicine", "Qty", "Order Date", "Delivery Date", "Status"]
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
            if self.status_filter.get() != "All":
                query["status"] = self.status_filter.get()
            
            skip = self.page_num * self.page_size
            orders = list(self.db.supplyOrders.find(query)
                         .sort("orderDate", -1)
                         .skip(skip).limit(self.page_size))
            
            for o in orders:
                supplier = self.db.suppliers.find_one({"_id": o.get("supplierId")}) or {}
                pharmacy = self.db.pharmacies.find_one({"_id": o.get("pharmacyId")}) or {}
                med = self.db.medicines.find_one({"_id": o.get("medicineId")}) or {}
                
                self.table.insert([
                    str(o.get("_id"))[:10],
                    supplier.get("companyName", "—")[:15],
                    pharmacy.get("name", "—").split("—")[-1].strip()[:15],
                    med.get("name", "—")[:15],
                    o.get("quantityOrdered", "—"),
                    o.get("orderDate", "—"),
                    o.get("deliveryDate", "—"),
                    o.get("status", "Pending"),
                ])
            
            total = self.db.supplyOrders.count_documents(query)
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self._load_data()

    def _next_page(self):
        self.page_num += 1
        self._load_data()


# ============================================================
# PAGE: ANALYTICS
# ============================================================
class AnalyticsPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="📊  Analytics Dashboard", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._build).pack(side="right")

        # Create scrollable canvas
        canvas = tk.Canvas(self, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Analytics sections
        self._top_medicines(scrollable_frame)
        self._prescription_status(scrollable_frame)
        self._supplier_performance(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True, padx=24, pady=16)
        scrollbar.pack(side="right", fill="y")

    def _top_medicines(self, parent):
        card = Card(parent)
        card.pack(fill="x", pady=(0, 16))
        SectionTitle(card, "Top 10 Prescribed Medicines").pack(anchor="w", padx=16, pady=(14, 8))
        
        try:
            pipeline = [
                {"$group": {"_id": "$medicineId", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10},
                {"$lookup": {"from": "medicines", "localField": "_id",
                             "foreignField": "_id", "as": "med"}},
                {"$unwind": "$med"},
            ]
            
            results = list(self.db.prescriptions.aggregate(pipeline))
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(10, 4))
            meds = [r["med"]["name"][:15] for r in results]
            counts = [r["count"] for r in results]
            
            ax.barh(meds, counts, color=COLORS["accent_light"])
            ax.set_xlabel("Number of Prescriptions", fontsize=10)
            ax.set_title("Top 10 Prescribed Medicines", fontsize=12, fontweight="bold")
            ax.invert_yaxis()
            fig.patch.set_facecolor(COLORS["bg_card"])
            ax.set_facecolor(COLORS["bg_card"])
            ax.tick_params(colors=COLORS["text_primary"])
            ax.xaxis.label.set_color(COLORS["text_primary"])
            
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        except Exception as e:
            tk.Label(card, text=f"Error: {str(e)}", fg=COLORS["danger"],
                     bg=COLORS["bg_card"]).pack(pady=16)

    def _prescription_status(self, parent):
        card = Card(parent)
        card.pack(fill="x", pady=(0, 16))
        SectionTitle(card, "Prescription Status Distribution").pack(anchor="w", padx=16, pady=(14, 8))
        
        try:
            statuses = list(self.db.prescriptions.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]))
            
            fig, ax = plt.subplots(figsize=(8, 4))
            labels = [s["_id"] for s in statuses]
            sizes = [s["count"] for s in statuses]
            colors = [COLORS["success"], COLORS["warning"], COLORS["danger"], COLORS["info"]][:len(labels)]
            
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
            ax.set_title("Prescription Status Distribution", fontsize=12, fontweight="bold")
            fig.patch.set_facecolor(COLORS["bg_card"])
            
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        except Exception as e:
            tk.Label(card, text=f"Error: {str(e)}", fg=COLORS["danger"],
                     bg=COLORS["bg_card"]).pack(pady=16)

    def _supplier_performance(self, parent):
        card = Card(parent)
        card.pack(fill="x")
        SectionTitle(card, "Supplier Performance").pack(anchor="w", padx=16, pady=(14, 8))
        
        try:
            pipeline = [
                {"$group": {"_id": "$supplierId", "orders": {"$sum": 1}, "totalValue": {"$sum": "$totalCost"}}},
                {"$sort": {"orders": -1}},
                {"$limit": 5},
                {"$lookup": {"from": "suppliers", "localField": "_id",
                             "foreignField": "_id", "as": "sup"}},
                {"$unwind": "$sup"},
            ]
            
            results = list(self.db.supplyOrders.aggregate(pipeline))
            
            fig, ax = plt.subplots(figsize=(10, 4))
            suppliers = [r["sup"]["companyName"][:12] for r in results]
            orders = [r["orders"] for r in results]
            
            ax.bar(suppliers, orders, color=COLORS["accent"])
            ax.set_ylabel("Number of Orders", fontsize=10)
            ax.set_title("Top Suppliers by Order Count", fontsize=12, fontweight="bold")
            fig.patch.set_facecolor(COLORS["bg_card"])
            ax.set_facecolor(COLORS["bg_card"])
            ax.tick_params(colors=COLORS["text_primary"])
            ax.yaxis.label.set_color(COLORS["text_primary"])
            
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        except Exception as e:
            tk.Label(card, text=f"Error: {str(e)}", fg=COLORS["danger"],
                     bg=COLORS["bg_card"]).pack(pady=16)


# ============================================================
# PAGE: QUERY LAB (Custom MongoDB Queries)
# ============================================================
class QueryLabPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🔍  Query Laboratory", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "Execute", self._execute_query,
                     color=COLORS["success"]).pack(side="right", padx=4)

        # Query input
        card = Card(self)
        card.pack(fill="x", padx=24, pady=12)
        tk.Label(card, text="MongoDB Aggregation Query (JSON):", font=FONTS["body"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(12, 6))
        
        self.query_text = scrolledtext.ScrolledText(card, font=FONTS["code"],
                                                     bg=COLORS["bg_dark"],
                                                     fg=COLORS["text_primary"],
                                                     insertbackground=COLORS["text_primary"],
                                                     height=10, width=80)
        self.query_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.query_text.insert("1.0", '[\n  {"$match": {"status": "Pending"}},\n  {"$limit": 10}\n]')

        # Collection selector
        sel_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        sel_frame.pack(fill="x", padx=24, pady=12)
        tk.Label(sel_frame, text="Collection:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        self.collection_var = tk.StringVar(value="prescriptions")
        ttk.Combobox(sel_frame, textvariable=self.collection_var,
                     values=["medicines", "pharmacies", "persons", "prescriptions",
                            "suppliers", "supplyOrders", "inventory"],
                     state="readonly", font=FONTS["body"], width=20).pack(side="left", padx=6)

        # Results
        card2 = Card(self)
        card2.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        tk.Label(card2, text="Results:", font=FONTS["body"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(12, 6))
        
        self.result_text = scrolledtext.ScrolledText(card2, font=FONTS["code"],
                                                      bg=COLORS["bg_dark"],
                                                      fg=COLORS["text_primary"],
                                                      state="disabled",
                                                      height=12, width=80)
        self.result_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def _execute_query(self):
        try:
            import json
            query_str = self.query_text.get("1.0", tk.END).strip()
            query = json.loads(query_str)
            
            collection_name = self.collection_var.get()
            collection = self.db[collection_name]
            
            results = list(collection.aggregate(query))
            
            # Format results
            results_json = json.dumps(results, indent=2, default=str)
            
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", f"Results ({len(results)} documents):\n\n{results_json}")
            self.result_text.config(state="disabled")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON: {str(e)}")
        except Exception as e:
            messagebox.showerror("Query Error", str(e))


# ============================================================
# PAGE: INDEXES
# ============================================================
class IndexesPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="⚡  Index Management", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        AccentButton(hdr, "↻ Refresh", self._refresh_indexes).pack(side="right", padx=4)

        # Index list
        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=16)
        
        control_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        control_frame.pack(fill="x", padx=24, pady=12)

        tk.Label(control_frame, text="Collection:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left")
        self.collection_var = tk.StringVar(value="medicines")
        ttk.Combobox(control_frame, textvariable=self.collection_var,
                     values=["medicines", "pharmacies", "persons", "prescriptions",
                             "suppliers", "supplyOrders", "inventory"],
                     width=22, state="readonly", font=FONTS["body"]).pack(side="left", padx=8)
        AccentButton(control_frame, "Refresh", self._refresh_indexes,
                     color=COLORS["info"]).pack(side="left", padx=4)

        self.index_text = scrolledtext.ScrolledText(card, font=FONTS["code"],
                                                     bg=COLORS["bg_dark"],
                                                     fg=COLORS["text_primary"],
                                                     height=15, width=80)
        self.index_text.pack(fill="both", expand=True, padx=16, pady=16)
        self._refresh_indexes()

    def _refresh_indexes(self):
        try:
            from database.indexes import IndexHelper
            helper = IndexHelper(self.db)
            collection_name = self.collection_var.get()
            indexes_info = helper.list_indexes_pretty(collection_name)
            
            self.index_text.config(state="normal")
            self.index_text.delete("1.0", tk.END)
            self.index_text.insert("1.0", f"Indexes for '{collection_name}':\n\n{indexes_info}")
            self.index_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ============================================================
# PAGE: OPTIMIZATION
# ============================================================
class OptimizationPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🔧  Database Optimization", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=16)
        
        info_text = scrolledtext.ScrolledText(card, font=FONTS["body"],
                                               bg=COLORS["bg_dark"],
                                               fg=COLORS["text_primary"],
                                               height=20, width=80)
        info_text.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Display optimization info
        try:
            info = self.db.command("dbStats")
            info_str = "Database Statistics:\n"
            info_str += f"Collections: {info.get('collections')}\n"
            info_str += f"Data Size: {info.get('dataSize')} bytes\n"
            info_str += f"Index Size: {info.get('indexSize')} bytes\n"
            info_str += f"Storage Size: {info.get('storageSize')} bytes\n\n"
            info_str += "Optimization Tips:\n"
            info_str += "1. Create indexes on frequently queried fields\n"
            info_str += "2. Monitor slow queries using profiling\n"
            info_str += "3. Archive old data periodically\n"
            info_str += "4. Use projection to limit returned fields\n"
            info_str += "5. Batch write operations for bulk inserts\n"
            
            info_text.insert("1.0", info_str)
        except Exception as e:
            info_text.insert("1.0", f"Error: {str(e)}")
        
        info_text.config(state="disabled")


# ============================================================
# PAGE: BACKUP/RESTORE
# ============================================================
class BackupRestorePage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🗄️  Backup & Restore", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")

        # Buttons
        btn_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=24, pady=16)
        AccentButton(btn_frame, "💾  Create Backup", self._create_backup,
                     color=COLORS["success"]).pack(side="left", padx=4)
        AccentButton(btn_frame, "📂  Restore Backup", self._restore_backup,
                     color=COLORS["warning"]).pack(side="left", padx=4)

        # Log
        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        tk.Label(card, text="Operation Log:", font=FONTS["body"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(12, 6))
        
        self.log_text = scrolledtext.ScrolledText(card, font=FONTS["code"],
                                                   bg=COLORS["bg_dark"],
                                                   fg=COLORS["text_primary"],
                                                   height=12, width=80)
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.log_text.insert("1.0", "Backup/Restore operations will be logged here...\n")

    def _create_backup(self):
        try:
            from database.backup_restore import BackupRestoreHelper
            helper = BackupRestoreHelper()
            self.log_text.insert(tk.END, "Starting backup...\n")
            helper.backup()
            self.log_text.insert(tk.END, "Backup completed successfully!\n")
            messagebox.showinfo("Success", "Backup created successfully!")
        except Exception as e:
            self.log_text.insert(tk.END, f"Error: {str(e)}\n")
            messagebox.showerror("Error", str(e))

    def _restore_backup(self):
        try:
            from database.backup_restore import BackupRestoreHelper
            helper = BackupRestoreHelper()
            self.log_text.insert(tk.END, "Starting restore...\n")
            helper.restore()
            self.log_text.insert(tk.END, "Restore completed successfully!\n")
            messagebox.showinfo("Success", "Restore completed successfully!")
        except Exception as e:
            self.log_text.insert(tk.END, f"Error: {str(e)}\n")
            messagebox.showerror("Error", str(e))


# ============================================================
# PAGE: TRANSACTIONS
# ============================================================
class TransactionPrescriptionPage(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db = db
        self.pending_prescriptions = []
        self._build()
        self._load_prescriptions()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="🔒  Transaction Test", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")

        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=16)

        info = scrolledtext.ScrolledText(card, font=FONTS["body"],
                                          bg=COLORS["bg_dark"],
                                          fg=COLORS["text_primary"],
                                          height=10, width=80)
        info.pack(fill="both", expand=True, padx=16, pady=(16, 8))

        info_str = "ACID Transactions for Prescription Dispensing\n"
        info_str += "=" * 50 + "\n\n"
        info_str += "Transaction ensures:\n"
        info_str += "1. Atomicity: All or nothing\n"
        info_str += "2. Consistency: Database stays valid\n"
        info_str += "3. Isolation: No interference\n"
        info_str += "4. Durability: Persisted changes\n\n"
        info_str += "Dispensing Process:\n"
        info_str += "- Check inventory stock\n"
        info_str += "- Validate minimum thresholds\n"
        info_str += "- Decrement stock atomically\n"
        info_str += "- Mark prescription as dispensed\n\n"
        info_str += "Note: Requires MongoDB Replica Set\n"
        info_str += "For standalone: Fallback to non-transactional mode\n"

        info.insert("1.0", info_str)
        info.config(state="disabled")

        controls = tk.Frame(card, bg=COLORS["bg_card"])
        controls.pack(fill="x", padx=16, pady=(0, 12))

        tk.Label(controls, text="Pending Prescription:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(side="left")
        self.selected_rx = tk.StringVar()
        self.prescription_box = ttk.Combobox(controls, textvariable=self.selected_rx,
                                            values=[], width=52, state="readonly",
                                            font=FONTS["body"])
        self.prescription_box.pack(side="left", padx=8)
        AccentButton(controls, "Refresh", self._load_prescriptions,
                     color=COLORS["info"]).pack(side="left", padx=4)
        AccentButton(controls, "Dispense", self._dispense_transaction,
                     color=COLORS["accent"]).pack(side="left", padx=4)

        log_card = Card(self)
        log_card.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        tk.Label(log_card, text="Transaction Log:", font=FONTS["body"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(12, 6))

        self.log_text = scrolledtext.ScrolledText(log_card, font=FONTS["code"],
                                                   bg=COLORS["bg_dark"],
                                                   fg=COLORS["text_primary"],
                                                   height=10, width=80)
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._append_log('Ready to process pending prescriptions. Click Refresh to load list.')

    def _append_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} — {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _load_prescriptions(self):
        try:
            docs = list(self.db.prescriptions.find({"status": "Pending"}).limit(50))
            self.pending_prescriptions = docs
            choices = [
                f"{str(doc['_id'])[:8]} | {doc.get('patientName','Unknown')} | "
                f"{doc.get('medicineName','Unknown')} x{doc.get('quantity',1)}"
                for doc in docs
            ]
            self.prescription_box['values'] = choices
            if choices:
                self.prescription_box.current(0)
                self.selected_rx.set(choices[0])
                self._append_log(f"Loaded {len(choices)} pending prescriptions")
            else:
                self.prescription_box.set("")
                self._append_log("No pending prescriptions found")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            self._append_log(f"Load failed: {e}")

    def _dispense_transaction(self):
        idx = self.prescription_box.current()
        if idx < 0 or idx >= len(self.pending_prescriptions):
            messagebox.showwarning("Selection Required", "Please select a pending prescription first.")
            return

        prescription = self.pending_prescriptions[idx]
        rx_id = prescription['_id']
        med_id = prescription.get('medicineId')
        pha_id = prescription.get('pharmacyId')
        qty = int(prescription.get('quantity', 1))

        try:
            from database.transactions import TransactionHelper, StandaloneError
            helper = TransactionHelper(self.db, DatabaseConnection.get_client())
            log = helper.dispense(rx_id, med_id, pha_id, qty)
            for line in log:
                self._append_log(line)
            messagebox.showinfo("Success", "Prescription dispensed successfully using transaction.")
            self._load_prescriptions()
        except StandaloneError as e:
            self._append_log(f"Replica set unavailable: {e}")
            if messagebox.askyesno("Fallback Dispense", "Transactions are not supported on this MongoDB instance. Run fallback dispense anyway?"):
                self._fallback_dispense()
        except ValueError as e:
            self._append_log(f"Transaction failed: {e}")
            messagebox.showerror("Transaction Failed", str(e))
        except Exception as e:
            self._append_log(f"Unexpected error: {e}")
            messagebox.showerror("Error", str(e))

    def _fallback_dispense(self):
        idx = self.prescription_box.current()
        if idx < 0 or idx >= len(self.pending_prescriptions):
            messagebox.showwarning("Selection Required", "Please select a pending prescription first.")
            return

        prescription = self.pending_prescriptions[idx]
        rx_id = prescription['_id']
        med_id = prescription.get('medicineId')
        pha_id = prescription.get('pharmacyId')
        qty = int(prescription.get('quantity', 1))

        try:
            inv = self.db.inventory.find_one({"medicineId": med_id, "pharmacyId": pha_id})
            if not inv:
                raise ValueError("Inventory record not found for selected prescription.")
            current = inv.get('currentStock', 0)
            if current < qty:
                raise ValueError(f"Insufficient stock for fallback dispense. Available: {current}")

            self.db.inventory.update_one({"_id": inv['_id']}, {"$inc": {"currentStock": -qty}})
            self.db.prescriptions.update_one({"_id": rx_id}, {"$set": {
                "status": "Dispensed",
                "dispensedAt": datetime.now()
            }})
            self._append_log("Fallback dispense completed successfully")
            messagebox.showinfo("Success", "Prescription dispensed successfully using fallback logic.")
            self._load_prescriptions()
        except Exception as e:
            self._append_log(f"Fallback failed: {e}")
            messagebox.showerror("Fallback Error", str(e))
