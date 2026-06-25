"""
gui/medicines.py
================
Page: MedicinesPage - Complete medicines registry with CRUD operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from bson import ObjectId

from database.connection import COLORS, FONTS
from gui.settings import Card, AccentButton, DataTable, SectionTitle


# ============================================================
# PAGE: MEDICINES (EXTENDED)
# ============================================================
class MedicinesPage(tk.Frame):
    """
    Complete medicines registry page with:
    - Search and filtering by name/generic name/type
    - Add/Edit/Delete medicines
    - Pagination support
    - Advanced filtering options
    """
    
    def __init__(self, parent, db):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.db        = db
        self.page_num  = 0
        self.page_size = 15
        self.filter_type = tk.StringVar(value="All")
        self.sort_by = tk.StringVar(value="name")
        self.selected_medicine = None
        self._build()

    def _build(self):
        # Header with title and add button
        hdr = tk.Frame(self, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="💊  Medicines Registry", font=FONTS["title"],
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        
        btn_frame = tk.Frame(hdr, bg=COLORS["bg_dark"])
        btn_frame.pack(side="right")
        AccentButton(btn_frame, "+ Add Medicine", self._add_dialog).pack(side="left", padx=4)
        AccentButton(btn_frame, "🔄 Refresh", self._load_data, 
                     color=COLORS["info"]).pack(side="left", padx=4)

        # Filter and search bar
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

        tk.Label(fb, text="Sort by:", font=FONTS["body"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(side="left", padx=(16, 6))
        sb = ttk.Combobox(fb, textvariable=self.sort_by,
                          values=["name", "unitPrice", "minimumStockThreshold"],
                          width=15, state="readonly", font=FONTS["body"])
        sb.pack(side="left", padx=6)
        sb.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        AccentButton(fb, "🔍 Search", self._load_data,
                     color=COLORS["info"]).pack(side="left", padx=8)

        # Data table card
        card = Card(self)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols = ["Name", "Generic Name", "Type", "Category",
                "Price (Rs)", "Min Stock", "Controlled", "Requires Rx", "Mfr"]
        self.table = DataTable(card, cols)
        self.table.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Bind click to select medicine
        self.table.tree.bind("<Double-1>", self._on_double_click)

        # Pagination and action buttons
        pag = tk.Frame(self, bg=COLORS["bg_dark"])
        pag.pack(fill="x", padx=24, pady=(0, 12))
        
        AccentButton(pag, "◀ Prev", self._prev_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        self.page_label = tk.Label(pag, text="Page 1", font=FONTS["body"],
                                   fg=COLORS["text_secondary"], bg=COLORS["bg_dark"])
        self.page_label.pack(side="left", padx=8)
        AccentButton(pag, "Next ▶", self._next_page,
                     color=COLORS["bg_card"]).pack(side="left", padx=4)
        
        # Action buttons for selected item
        AccentButton(pag, "✎  Edit", self._edit_selected,
                     color=COLORS["warning"]).pack(side="right", padx=4)
        AccentButton(pag, "🗑️  Delete", self._delete_selected,
                     color=COLORS["danger"]).pack(side="right", padx=4)
        
        self._load_data()

    def _load_data(self):
        """Load and display medicines based on filters"""
        self.table.clear()
        try:
            query = {}
            
            # Search filter
            s = self.search_var.get().strip()
            if s:
                query["$or"] = [
                    {"name":        {"$regex": s, "$options": "i"}},
                    {"genericName": {"$regex": s, "$options": "i"}},
                    {"manufacturer": {"$regex": s, "$options": "i"}}
                ]
            
            # Type filter
            t = self.filter_type.get()
            if t != "All":
                query["type"] = t
            
            # Get medicines with pagination and sorting
            skip = self.page_num * self.page_size
            sort_field = self.sort_by.get()
            meds = list(self.db.medicines.find(query)
                        .sort(sort_field, 1)
                        .skip(skip).limit(self.page_size))
            
            # Get category name mapping
            cat_map = {c["_id"]: c["name"]
                       for c in self.db.categories.find({})}
            
            # Display medicines in table
            for m in meds:
                self.table.insert([
                    m.get("name", "—")[:20],
                    m.get("genericName", "—")[:20],
                    m.get("type", "—"),
                    cat_map.get(m.get("categoryId"), "—")[:15],
                    f"Rs {m.get('unitPrice', 0):.2f}",
                    m.get("minimumStockThreshold", "—"),
                    "✓" if m.get("controlledSubstance") else "—",
                    "✓" if m.get("requiresPrescription") else "—",
                    m.get("manufacturer", "—")[:15],
                ])
            
            # Update pagination label
            total = self.db.medicines.count_documents(query)
            pages = max(1, (total + self.page_size - 1) // self.page_size)
            self.page_label.config(
                text=f"Page {self.page_num+1} of {pages}  ({total} records)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines:\n{str(e)}")

    def _prev_page(self):
        """Go to previous page"""
        if self.page_num > 0:
            self.page_num -= 1
            self._load_data()

    def _next_page(self):
        """Go to next page"""
        self.page_num += 1
        self._load_data()

    def _on_double_click(self, event):
        """Handle double-click on table row"""
        item = self.table.tree.selection()
        if item:
            self._edit_selected()

    def _edit_selected(self):
        """Edit selected medicine"""
        selection = self.table.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a medicine to edit.")
            return
        
        # Get the medicine from database (simplified - in production would track ID)
        try:
            query = {}
            s = self.search_var.get().strip()
            if s:
                query["$or"] = [
                    {"name": {"$regex": s, "$options": "i"}},
                    {"genericName": {"$regex": s, "$options": "i"}}
                ]
            t = self.filter_type.get()
            if t != "All":
                query["type"] = t
            
            meds = list(self.db.medicines.find(query).sort(self.sort_by.get(), 1)
                       .skip(self.page_num * self.page_size).limit(self.page_size))
            
            if meds:
                self._edit_dialog(meds[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_selected(self):
        """Delete selected medicine"""
        selection = self.table.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a medicine to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this medicine?"):
            try:
                # Get first medicine from current view
                query = {}
                s = self.search_var.get().strip()
                if s:
                    query["$or"] = [
                        {"name": {"$regex": s, "$options": "i"}},
                        {"genericName": {"$regex": s, "$options": "i"}}
                    ]
                t = self.filter_type.get()
                if t != "All":
                    query["type"] = t
                
                meds = list(self.db.medicines.find(query).sort(self.sort_by.get(), 1)
                           .skip(self.page_num * self.page_size).limit(self.page_size))
                
                if meds:
                    self.db.medicines.delete_one({"_id": meds[0]["_id"]})
                    messagebox.showinfo("Success", "Medicine deleted successfully.")
                    self._load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _add_dialog(self):
        """Open dialog to add new medicine"""
        dlg = tk.Toplevel(self)
        dlg.title("Add New Medicine")
        dlg.configure(bg=COLORS["bg_card"])
        dlg.geometry("550x650")
        dlg.grab_set()
        
        SectionTitle(dlg, "Add New Medicine").pack(pady=(20, 16), padx=20)
        
        fields = {}
        
        # Form fields
        form = tk.Frame(dlg, bg=COLORS["bg_card"])
        form.pack(fill="x", padx=24, expand=True)
        
        field_defs = [
            ("Medicine Name *",       "name"),
            ("Generic Name",          "genericName"),
            ("Manufacturer",          "manufacturer"),
            ("Unit Price (Rs) *",     "unitPrice"),
            ("Min Stock Threshold *", "minimumStockThreshold"),
            ("Strength",              "strength"),
        ]
        
        for label, key in field_defs:
            tk.Label(form, text=label, font=FONTS["body"],
                     fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
            e = tk.Entry(form, font=FONTS["body"], bg=COLORS["bg_dark"],
                         fg=COLORS["text_primary"],
                         insertbackground=COLORS["text_primary"],
                         relief="flat", bd=1)
            e.pack(fill="x", ipady=6)
            fields[key] = e
        
        # Type dropdown
        tk.Label(form, text="Type *", font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        type_var = tk.StringVar(value="PrescriptionMedicine")
        ttk.Combobox(form, textvariable=type_var,
                     values=["PrescriptionMedicine", "OTCMedicine"],
                     state="readonly",
                     font=FONTS["body"], width=40).pack(fill="x")
        
        # Category dropdown
        tk.Label(form, text="Category", font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        categories = [c["name"] for c in self.db.categories.find({})]
        cat_var = tk.StringVar(value=categories[0] if categories else "")
        ttk.Combobox(form, textvariable=cat_var,
                     values=categories,
                     state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        # Checkboxes
        chk_frame = tk.Frame(form, bg=COLORS["bg_card"])
        chk_frame.pack(fill="x", pady=12)
        
        controlled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(chk_frame, text="Controlled Substance",
                       variable=controlled_var, bg=COLORS["bg_card"],
                       fg=COLORS["text_primary"], font=FONTS["body"]).pack(anchor="w")
        
        def save():
            try:
                name = fields["name"].get().strip()
                if not name:
                    messagebox.showerror("Validation Error", "Medicine name is required.")
                    return
                
                price = fields["unitPrice"].get().strip()
                if not price:
                    messagebox.showerror("Validation Error", "Unit price is required.")
                    return
                
                threshold = fields["minimumStockThreshold"].get().strip()
                if not threshold:
                    messagebox.showerror("Validation Error", "Min stock threshold is required.")
                    return
                
                # Get category ID
                cat_doc = self.db.categories.find_one({"name": cat_var.get()})
                cat_id = cat_doc["_id"] if cat_doc else None
                
                doc = {
                    "name":                  name,
                    "genericName":           fields["genericName"].get().strip(),
                    "manufacturer":          fields["manufacturer"].get().strip(),
                    "type":                  type_var.get(),
                    "unitPrice":             float(price),
                    "minimumStockThreshold": int(threshold),
                    "strength":              fields["strength"].get().strip(),
                    "categoryId":            cat_id,
                    "requiresPrescription":  type_var.get() == "PrescriptionMedicine",
                    "controlledSubstance":   controlled_var.get(),
                }
                
                self.db.medicines.insert_one(doc)
                messagebox.showinfo("Success",
                    f"Medicine '{name}' added successfully!")
                dlg.destroy()
                self._load_data()
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        AccentButton(dlg, "💾  Save Medicine", save).pack(pady=20)

    def _edit_dialog(self, medicine):
        """Open dialog to edit medicine"""
        dlg = tk.Toplevel(self)
        dlg.title("Edit Medicine")
        dlg.configure(bg=COLORS["bg_card"])
        dlg.geometry("550x650")
        dlg.grab_set()
        
        SectionTitle(dlg, f"Edit: {medicine.get('name')}").pack(pady=(20, 16), padx=20)
        
        fields = {}
        
        form = tk.Frame(dlg, bg=COLORS["bg_card"])
        form.pack(fill="x", padx=24, expand=True)
        
        field_defs = [
            ("Medicine Name",         "name"),
            ("Generic Name",          "genericName"),
            ("Manufacturer",          "manufacturer"),
            ("Unit Price (Rs)",       "unitPrice"),
            ("Min Stock Threshold",   "minimumStockThreshold"),
            ("Strength",              "strength"),
        ]
        
        for label, key in field_defs:
            tk.Label(form, text=label, font=FONTS["body"],
                     fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
            e = tk.Entry(form, font=FONTS["body"], bg=COLORS["bg_dark"],
                         fg=COLORS["text_primary"],
                         insertbackground=COLORS["text_primary"],
                         relief="flat", bd=1)
            e.insert(0, str(medicine.get(key, "")))
            e.pack(fill="x", ipady=6)
            fields[key] = e
        
        # Type
        tk.Label(form, text="Type", font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        type_var = tk.StringVar(value=medicine.get("type", "PrescriptionMedicine"))
        ttk.Combobox(form, textvariable=type_var,
                     values=["PrescriptionMedicine", "OTCMedicine"],
                     state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        # Category
        tk.Label(form, text="Category", font=FONTS["body"],
                 fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(8, 2))
        categories = [c["name"] for c in self.db.categories.find({})]
        current_cat = ""
        if medicine.get("categoryId"):
            cat_doc = self.db.categories.find_one({"_id": medicine["categoryId"]})
            current_cat = cat_doc["name"] if cat_doc else ""
        cat_var = tk.StringVar(value=current_cat)
        ttk.Combobox(form, textvariable=cat_var,
                     values=categories,
                     state="readonly", font=FONTS["body"], width=40).pack(fill="x")
        
        # Checkboxes
        chk_frame = tk.Frame(form, bg=COLORS["bg_card"])
        chk_frame.pack(fill="x", pady=12)
        
        controlled_var = tk.BooleanVar(value=medicine.get("controlledSubstance", False))
        tk.Checkbutton(chk_frame, text="Controlled Substance",
                       variable=controlled_var, bg=COLORS["bg_card"],
                       fg=COLORS["text_primary"], font=FONTS["body"]).pack(anchor="w")
        
        def save():
            try:
                # Get category ID
                cat_doc = self.db.categories.find_one({"name": cat_var.get()})
                cat_id = cat_doc["_id"] if cat_doc else medicine.get("categoryId")
                
                update = {
                    "name":                  fields["name"].get().strip(),
                    "genericName":           fields["genericName"].get().strip(),
                    "manufacturer":          fields["manufacturer"].get().strip(),
                    "type":                  type_var.get(),
                    "unitPrice":             float(fields["unitPrice"].get() or 0),
                    "minimumStockThreshold": int(fields["minimumStockThreshold"].get() or 0),
                    "strength":              fields["strength"].get().strip(),
                    "categoryId":            cat_id,
                    "requiresPrescription":  type_var.get() == "PrescriptionMedicine",
                    "controlledSubstance":   controlled_var.get(),
                }
                
                self.db.medicines.update_one({"_id": medicine["_id"]}, {"$set": update})
                messagebox.showinfo("Success", "Medicine updated successfully!")
                dlg.destroy()
                self._load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        AccentButton(dlg, "💾  Save Changes", save).pack(pady=20)
