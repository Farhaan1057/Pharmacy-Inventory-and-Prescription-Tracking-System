"""
database/crud.py
================
Helper methods wrapping common CRUD operations.
Used by GUI pages to keep database logic separate from UI code.
"""

from datetime import datetime
from bson import ObjectId


class CRUDHelper:
    """
    Wraps insert / find / update / delete operations for all collections.
    Pass the db object (from DatabaseConnection.get_db()) on construction.
    """

    def __init__(self, db):
        self.db = db

    # ── MEDICINES ────────────────────────────────────────────
    def get_medicines(self, query=None, skip=0, limit=15):
        return list(self.db.medicines.find(query or {}).skip(skip).limit(limit))

    def count_medicines(self, query=None):
        return self.db.medicines.count_documents(query or {})

    def insert_medicine(self, doc: dict):
        return self.db.medicines.insert_one(doc)

    def update_medicine(self, med_id, update: dict):
        return self.db.medicines.update_one({"_id": med_id}, {"$set": update})

    def delete_medicine(self, med_id):
        return self.db.medicines.delete_one({"_id": med_id})

    # ── INVENTORY ────────────────────────────────────────────
    def adjust_stock(self, medicine_name: str, delta: int):
        """Increment (or decrement if negative) stock for all pharmacies."""
        med = self.db.medicines.find_one(
            {"name": {"$regex": medicine_name, "$options": "i"}})
        if not med:
            raise ValueError(f"Medicine '{medicine_name}' not found.")
        result = self.db.inventory.update_many(
            {"medicineId": med["_id"]},
            {"$inc": {"currentStock": delta}})
        return result.modified_count

    def get_low_stock(self):
        return list(self.db.inventory.find(
            {"$expr": {"$lt": ["$currentStock", "$minimumThreshold"]}}))

    def get_near_expiry(self, days=90):
        from datetime import timedelta
        cutoff = datetime.now() + timedelta(days=days)
        return list(self.db.inventory.find(
            {"batches.expiryDate": {"$lte": cutoff}}))

    # ── PRESCRIPTIONS ────────────────────────────────────────
    def get_prescriptions(self, query=None, skip=0, limit=12, sort_field="prescriptionDate"):
        return list(
            self.db.prescriptions
                .find(query or {})
                .sort(sort_field, -1)
                .skip(skip)
                .limit(limit))

    def count_prescriptions(self, query=None):
        return self.db.prescriptions.count_documents(query or {})

    def insert_prescription(self, doc: dict):
        doc.setdefault("prescriptionDate", datetime.now())
        doc.setdefault("status", "Pending")
        doc.setdefault("isControlledSubstance", False)
        return self.db.prescriptions.insert_one(doc)

    def dispense_prescription(self, rx_id, medicine_id, pharmacy_id, qty: int):
        """
        Non-transactional dispense (fallback for standalone mongod).
        Returns (success: bool, message: str).
        """
        inv = self.db.inventory.find_one(
            {"medicineId": medicine_id, "pharmacyId": pharmacy_id})
        if not inv:
            return False, "No inventory record found."
        current = inv.get("currentStock", 0)
        if current < qty:
            return False, f"Insufficient stock: {current} available, {qty} requested."
        self.db.inventory.update_one(
            {"_id": inv["_id"]}, {"$inc": {"currentStock": -qty}})
        self.db.prescriptions.update_one(
            {"_id": rx_id},
            {"$set": {"status": "Dispensed", "dispensedAt": datetime.now()}})
        return True, f"Dispensed {qty} units. Stock: {current} → {current - qty}."

    # ── SUPPLY ORDERS ────────────────────────────────────────
    def get_orders(self, query=None, skip=0, limit=15):
        return list(self.db.supplyOrders.find(query or {}).skip(skip).limit(limit))

    def count_orders(self, query=None):
        return self.db.supplyOrders.count_documents(query or {})

    # ── PERSONS ──────────────────────────────────────────────
    def get_persons(self, role=None, skip=0, limit=15):
        query = {"roles": role} if role else {}
        return list(self.db.persons.find(query).skip(skip).limit(limit))

    def get_person_map(self):
        """Returns {_id: name} dict for all persons."""
        return {p["_id"]: p.get("name", "?") for p in self.db.persons.find({})}

    # ── DASHBOARD STATS ──────────────────────────────────────
    def get_dashboard_stats(self):
        from datetime import timedelta
        try:
            ninety = datetime.now() + timedelta(days=90)
            return {
                "medicines":     self.db.medicines.count_documents({}),
                "pharmacies":    self.db.pharmacies.count_documents({}),
                "prescriptions": self.db.prescriptions.count_documents({}),
                "inventory":     self.db.inventory.count_documents({}),
                "low_stock":     self.db.inventory.count_documents(
                    {"$expr": {"$lt": ["$currentStock", "$minimumThreshold"]}}),
                "near_expiry":   self.db.inventory.count_documents(
                    {"batches.expiryDate": {"$lte": ninety}}),
            }
        except Exception:
            return {k: 0 for k in
                    ["medicines", "pharmacies", "prescriptions",
                     "inventory", "low_stock", "near_expiry"]}