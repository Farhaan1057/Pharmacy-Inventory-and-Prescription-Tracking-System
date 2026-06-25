"""
database/aggregations.py
========================
All aggregation pipelines used in the Analytics and Query Lab tabs.
Each method returns a list of result documents.
"""

from datetime import datetime, timedelta


class AggregationPipelines:
    """
    12 aggregation pipelines covering all CSC316 lab requirements.
    Pass the db object (DatabaseConnection.get_db()) on construction.
    """

    def __init__(self, db):
        self.db = db

    # ── 1. Top Prescribed Medicines ──────────────────────────
    def top_medicines(self, limit=10):
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {
                "_id":      "$items.medicineName",
                "count":    {"$sum": 1},
                "totalQty": {"$sum": "$items.quantityPrescribed"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(self.db.prescriptions.aggregate(pipeline))

    # ── 2. Prescriptions per Doctor ──────────────────────────
    def prescriptions_per_doctor(self):
        pipeline = [
            {"$group": {"_id": "$doctorId", "total": {"$sum": 1}}},
            {"$lookup": {
                "from": "persons", "localField": "_id",
                "foreignField": "_id", "as": "doc"
            }},
            {"$project": {
                "name":  {"$arrayElemAt": ["$doc.name", 0]},
                "spec":  {"$arrayElemAt": ["$doc.doctorProfile.specialization", 0]},
                "total": 1
            }},
            {"$sort": {"total": -1}}
        ]
        return list(self.db.prescriptions.aggregate(pipeline))

    # ── 3. Stock Level per City / Branch ─────────────────────
    def stock_per_branch(self):
        pipeline = [
            {"$lookup": {
                "from": "pharmacies", "localField": "pharmacyId",
                "foreignField": "_id", "as": "pha"
            }},
            {"$group": {
                "_id":       {"$arrayElemAt": ["$pha.name", 0]},
                "city":      {"$first": {"$arrayElemAt": ["$pha.city", 0]}},
                "totalStock": {"$sum": "$currentStock"},
                "lowItems":   {"$sum": {
                    "$cond": [{"$lt": ["$currentStock", "$minimumThreshold"]}, 1, 0]
                }}
            }},
            {"$sort": {"totalStock": -1}}
        ]
        return list(self.db.inventory.aggregate(pipeline))

    # ── 4. Supplier Performance Ranking ──────────────────────
    def supplier_performance(self):
        pipeline = [
            {"$match": {"status": "Delivered"}},
            {"$group": {
                "_id":    "$supplierId",
                "orders": {"$sum": 1},
                "value":  {"$sum": "$totalAmount"}
            }},
            {"$lookup": {
                "from": "suppliers", "localField": "_id",
                "foreignField": "_id", "as": "sup"
            }},
            {"$project": {
                "name":   {"$arrayElemAt": ["$sup.name", 0]},
                "score":  {"$arrayElemAt": ["$sup.reliabilityScore", 0]},
                "orders": 1, "value": 1
            }},
            {"$sort": {"score": -1}}
        ]
        return list(self.db.supplyOrders.aggregate(pipeline))

    # ── 5. Delivery Brackets ($switch) ───────────────────────
    def delivery_brackets(self):
        pipeline = [
            {"$match": {"status": "Delivered"}},
            {"$project": {
                "DELIVERY_BRACKET": {"$switch": {
                    "branches": [
                        {"case": {"$lte": [
                            {"$subtract": ["$deliveryDate", "$orderDate"]},
                            172800000]},
                         "then": "Within 2 days"},
                        {"case": {"$lte": [
                            {"$subtract": ["$deliveryDate", "$orderDate"]},
                            432000000]},
                         "then": "3-5 days"}
                    ],
                    "default": "More than 5 days"
                }},
                "totalAmount": 1
            }},
            {"$group": {
                "_id":   "$DELIVERY_BRACKET",
                "count": {"$sum": 1},
                "value": {"$sum": "$totalAmount"}
            }},
            {"$sort": {"count": -1}}
        ]
        return list(self.db.supplyOrders.aggregate(pipeline))

    # ── 6. Prescription Status Distribution ──────────────────
    def prescription_status_distribution(self):
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        return list(self.db.prescriptions.aggregate(pipeline))

    # ── 7. Controlled Substance Flags ────────────────────────
    def controlled_substance_patients(self, min_count=2):
        pipeline = [
            {"$match": {"isControlledSubstance": True}},
            {"$group": {"_id": "$patientId", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": min_count}}},
            {"$lookup": {
                "from": "persons", "localField": "_id",
                "foreignField": "_id", "as": "patient"
            }},
            {"$project": {
                "_id": 0,
                "patientName": {"$arrayElemAt": ["$patient.name", 0]},
                "count": 1,
                "flag": "REVIEW REQUIRED"
            }}
        ]
        return list(self.db.prescriptions.aggregate(pipeline))

    # ── 8. Revenue per Pharmacy ───────────────────────────────
    def revenue_per_pharmacy(self):
        pipeline = [
            {"$match": {"status": "Delivered"}},
            {"$group": {
                "_id":         "$pharmacyId",
                "totalSpent":  {"$sum": "$totalAmount"},
                "totalOrders": {"$sum": 1}
            }},
            {"$lookup": {
                "from": "pharmacies", "localField": "_id",
                "foreignField": "_id", "as": "pha"
            }},
            {"$project": {
                "_id": 0,
                "pharmacyName": {"$arrayElemAt": ["$pha.name", 0]},
                "city":         {"$arrayElemAt": ["$pha.city", 0]},
                "totalSpent": 1, "totalOrders": 1,
                "avgOrderValue": {"$divide": ["$totalSpent", "$totalOrders"]}
            }},
            {"$sort": {"totalSpent": -1}}
        ]
        return list(self.db.supplyOrders.aggregate(pipeline))

    # ── 9. Restocking Recommendations ────────────────────────
    def restock_recommendations(self):
        pipeline = [
            {"$match": {"$expr": {"$lt": ["$currentStock", "$minimumThreshold"]}}},
            {"$lookup": {
                "from": "medicines", "localField": "medicineId",
                "foreignField": "_id", "as": "med"
            }},
            {"$lookup": {
                "from": "pharmacies", "localField": "pharmacyId",
                "foreignField": "_id", "as": "pha"
            }},
            {"$project": {
                "_id": 0,
                "medicineName":       {"$arrayElemAt": ["$med.name", 0]},
                "pharmacyName":       {"$arrayElemAt": ["$pha.name", 0]},
                "currentStock":       1,
                "shortfall":          {"$subtract": ["$minimumThreshold", "$currentStock"]},
                "recommendedOrderQty": {"$multiply": [
                    {"$subtract": ["$minimumThreshold", "$currentStock"]}, 2]},
                "orderStatus": "AUTO-GENERATED"
            }}
        ]
        return list(self.db.inventory.aggregate(pipeline))

    # ── 10. Low Stock Alert (with $lookup) ───────────────────
    def low_stock_alert(self):
        pipeline = [
            {"$match": {"$expr": {"$lt": ["$currentStock", "$minimumThreshold"]}}},
            {"$lookup": {
                "from": "medicines", "localField": "medicineId",
                "foreignField": "_id", "as": "med"
            }},
            {"$lookup": {
                "from": "pharmacies", "localField": "pharmacyId",
                "foreignField": "_id", "as": "pha"
            }},
            {"$project": {
                "_id": 0,
                "medicineName":    {"$arrayElemAt": ["$med.name", 0]},
                "pharmacyName":    {"$arrayElemAt": ["$pha.name", 0]},
                "city":            {"$arrayElemAt": ["$pha.city", 0]},
                "currentStock":    1,
                "minimumThreshold": 1,
                "shortfall":       {"$subtract": ["$minimumThreshold", "$currentStock"]}
            }},
            {"$sort": {"shortfall": -1}}
        ]
        return list(self.db.inventory.aggregate(pipeline))

    # ── 11. Near-Expiry Batches ───────────────────────────────
    def near_expiry_batches(self, days=90):
        cutoff = datetime.now() + timedelta(days=days)
        pipeline = [
            {"$unwind": "$batches"},
            {"$match": {"batches.expiryDate": {"$lte": cutoff}}},
            {"$lookup": {
                "from": "medicines", "localField": "medicineId",
                "foreignField": "_id", "as": "med"
            }},
            {"$project": {
                "_id": 0,
                "medicineName":   {"$arrayElemAt": ["$med.name", 0]},
                "batchNumber":    "$batches.batchNumber",
                "expiryDate":     "$batches.expiryDate",
                "quantityAtRisk": "$batches.quantityRemaining"
            }},
            {"$sort": {"expiryDate": 1}}
        ]
        return list(self.db.inventory.aggregate(pipeline))

    # ── 12. Controlled-Substance Percentage ($project + $divide) ─
    def controlled_substance_stats(self):
        pipeline = [
            {"$group": {
                "_id": None,
                "total":      {"$sum": 1},
                "controlled": {"$sum": {"$cond": ["$isControlledSubstance", 1, 0]}}
            }},
            {"$project": {
                "total": 1, "controlled": 1,
                "pct":   {"$multiply": [
                    {"$divide": ["$controlled", "$total"]}, 100]}
            }}
        ]
        result = list(self.db.prescriptions.aggregate(pipeline))
        return result[0] if result else {}