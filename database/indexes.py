"""
database/indexes.py
===================
Helpers for creating, listing, dropping indexes and running
explain() plans.  Used by gui/indexes.py.
"""

import json
from pymongo import ASCENDING, DESCENDING, TEXT


class IndexHelper:
    """
    Wraps index management operations.
    Pass the db object (DatabaseConnection.get_db()) on construction.
    """

    COLLECTIONS = [
        "medicines", "pharmacies", "persons",
        "inventory", "prescriptions", "supplyOrders", "suppliers"
    ]

    def __init__(self, db):
        self.db = db

    # ── LIST ─────────────────────────────────────────────────
    def list_indexes(self, collection: str) -> list:
        """Return all indexes on the given collection as dicts."""
        return [dict(idx) for idx in self.db[collection].list_indexes()]

    def list_indexes_pretty(self, collection: str) -> str:
        """Return a pretty-printed JSON string of all indexes."""
        indexes = self.list_indexes(collection)
        return "\n\n".join(
            json.dumps(idx, default=str, indent=2) for idx in indexes)

    # ── CREATE ───────────────────────────────────────────────
    def create_single(self, collection: str, field: str, name: str = None):
        opts = {"name": name} if name else {}
        self.db[collection].create_index([(field, ASCENDING)], **opts)

    def create_compound(self, collection: str, field_spec: str, name: str = None):
        """
        field_spec format: "field1:1,field2:-1"
        direction 1 = ASC, -1 = DESC
        """
        parts = []
        for part in field_spec.split(","):
            part = part.strip()
            if ":" in part:
                f, d = part.rsplit(":", 1)
                parts.append((f.strip(), int(d)))
            else:
                parts.append((part, ASCENDING))
        opts = {"name": name} if name else {}
        self.db[collection].create_index(parts, **opts)

    def create_text(self, collection: str, fields: str, name: str = None):
        """fields: comma-separated field names to include in text index."""
        field_list = [f.strip() for f in fields.split(",")]
        opts = {"name": name} if name else {}
        self.db[collection].create_index(
            [(f, TEXT) for f in field_list], **opts)

    def create_multikey(self, collection: str, field: str, name: str = None):
        """Multikey indexes are created automatically for array fields."""
        opts = {"name": name} if name else {}
        self.db[collection].create_index([(field, ASCENDING)], **opts)

    def create_ttl(self, collection: str, field: str,
                   expire_seconds: int = 2592000, name: str = None):
        """TTL index — auto-deletes documents after expire_seconds."""
        opts = {"name": name} if name else {}
        self.db[collection].create_index(
            [(field, ASCENDING)],
            expireAfterSeconds=expire_seconds, **opts)

    # ── DROP ─────────────────────────────────────────────────
    def drop_index(self, collection: str, index_name: str):
        self.db[collection].drop_index(index_name)

    # ── QUICK PRESETS ────────────────────────────────────────
    def quick_text_medicines(self):
        self.db.medicines.create_index(
            [("name", TEXT), ("genericName", TEXT)],
            name="MedicineTextSearch")

    def quick_compound_inventory(self):
        self.db.inventory.create_index(
            [("pharmacyId", ASCENDING), ("medicineId", ASCENDING)],
            name="PharmacyMedicineCompound", unique=True)

    def quick_multikey_persons(self):
        self.db.persons.create_index(
            [("roles", ASCENDING)], name="PersonRolesMultikey")

    def quick_expiry_index(self):
        self.db.inventory.create_index(
            [("batches.expiryDate", ASCENDING)], name="BatchExpiryIndex")

    def quick_ttl_orders(self):
        self.db.supplyOrders.create_index(
            [("orderDate", ASCENDING)],
            expireAfterSeconds=2592000,
            name="OrderTTLIndex")

    # ── EXPLAIN ──────────────────────────────────────────────
    def run_explain(self, collection: str, query: dict) -> dict:
        """
        Run explain("executionStats") on a find query.
        Returns the full explain output as a dict.
        """
        return self.db[collection].find(query).explain()

    @staticmethod
    def parse_explain(result: dict) -> dict:
        """Extract the key metrics from an explain() result."""
        ep = result.get("executionStats", {})
        qp = result.get("queryPlanner", {})
        wp = qp.get("winningPlan", {})
        stage = wp.get("stage", "?")
        return {
            "stage":       stage,
            "index_used":  stage == "IXSCAN" or "IXSCAN" in str(wp),
            "nReturned":   ep.get("nReturned", "?"),
            "docsExamined": ep.get("totalDocsExamined", "?"),
            "keysExamined": ep.get("totalKeysExamined", "?"),
            "execTimeMs":  ep.get("executionTimeMillis", "?"),
            "raw":         result,
        }