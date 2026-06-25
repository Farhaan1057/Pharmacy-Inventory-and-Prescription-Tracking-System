"""
database/setup_database.py
==========================
Initialize MongoDB database with collections, indexes, and sample data.
Run once before starting the application: python -m database.setup_database
"""

import sys
from datetime import datetime, timedelta
from bson import ObjectId

from database.connection import DatabaseConnection


def setup_database():
    """Initialize the pharmacy database with all collections and indexes."""
    
    print("=" * 60)
    print("PHARMACY INVENTORY & PRESCRIPTION SYSTEM - DATABASE SETUP")
    print("=" * 60)
    
    try:
        db = DatabaseConnection.get_db()
        print(f"\n✓ Connected to MongoDB: pharmacy_db")
        
        # Drop existing collections for fresh setup
        print("\n→ Clearing existing data...")
        for collection in db.list_collection_names():
            db[collection].drop()
        
        print("→ Creating collections and indexes...")
        
        # ========================
        # 1. CATEGORIES
        # ========================
        print("  ✓ Setting up Categories...")
        categories = [
            {"_id": ObjectId(), "name": "Antibiotics", "description": "Antibiotic medicines"},
            {"_id": ObjectId(), "name": "Painkillers", "description": "Pain relief medicines"},
            {"_id": ObjectId(), "name": "Vitamins", "description": "Vitamin supplements"},
            {"_id": ObjectId(), "name": "Allergy", "description": "Allergy medicines"},
            {"_id": ObjectId(), "name": "Digestive", "description": "Digestive system medicines"},
        ]
        db.categories.insert_many(categories)
        db.categories.create_index("name")
        
        # ========================
        # 2. MEDICINES
        # ========================
        print("  ✓ Setting up Medicines...")
        cat_ids = {c["name"]: c["_id"] for c in categories}
        medicines = [
            {
                "_id": ObjectId(),
                "name": "Amoxicillin 500mg",
                "genericName": "Amoxicillin",
                "manufacturer": "Pharma Ltd",
                "type": "PrescriptionMedicine",
                "categoryId": cat_ids["Antibiotics"],
                "unitPrice": 450.00,
                "minimumStockThreshold": 50,
                "strength": "500mg",
                "requiresPrescription": True,
                "controlledSubstance": False,
            },
            {
                "_id": ObjectId(),
                "name": "Paracetamol 500mg",
                "genericName": "Paracetamol",
                "manufacturer": "Health Corp",
                "type": "OTCMedicine",
                "categoryId": cat_ids["Painkillers"],
                "unitPrice": 25.00,
                "minimumStockThreshold": 100,
                "strength": "500mg",
                "requiresPrescription": False,
                "controlledSubstance": False,
            },
            {
                "_id": ObjectId(),
                "name": "Codeine Phosphate",
                "genericName": "Codeine",
                "manufacturer": "Pharma Plus",
                "type": "PrescriptionMedicine",
                "categoryId": cat_ids["Painkillers"],
                "unitPrice": 850.00,
                "minimumStockThreshold": 20,
                "strength": "30mg",
                "requiresPrescription": True,
                "controlledSubstance": True,
            },
            {
                "_id": ObjectId(),
                "name": "Vitamin D3 1000IU",
                "genericName": "Cholecalciferol",
                "manufacturer": "Wellness Inc",
                "type": "OTCMedicine",
                "categoryId": cat_ids["Vitamins"],
                "unitPrice": 150.00,
                "minimumStockThreshold": 75,
                "strength": "1000IU",
                "requiresPrescription": False,
                "controlledSubstance": False,
            },
            {
                "_id": ObjectId(),
                "name": "Cetirizine 10mg",
                "genericName": "Cetirizine",
                "manufacturer": "Allergy Care",
                "type": "OTCMedicine",
                "categoryId": cat_ids["Allergy"],
                "unitPrice": 200.00,
                "minimumStockThreshold": 60,
                "strength": "10mg",
                "requiresPrescription": False,
                "controlledSubstance": False,
            },
        ]
        db.medicines.insert_many(medicines)
        db.medicines.create_index([("name", 1)])
        db.medicines.create_index([("genericName", 1)])
        db.medicines.create_index([("type", 1)])
        
        med_ids = {m["name"]: m["_id"] for m in medicines}
        
        # ========================
        # 3. PHARMACIES
        # ========================
        print("  ✓ Setting up Pharmacies...")
        pharmacies = [
            {
                "_id": ObjectId(),
                "name": "MedLife Pharmacy — Lahore",
                "address": "123 Mall Road",
                "city": "Lahore",
                "phone": "042-1234567",
                "email": "lahore@medlife.pk",
                "licenseNumber": "PH-001",
                "manager": "Ali Ahmed",
                "established": 2015,
            },
            {
                "_id": ObjectId(),
                "name": "Health Center — Islamabad",
                "address": "456 F-7",
                "city": "Islamabad",
                "phone": "051-7654321",
                "email": "islamabad@healthcenter.pk",
                "licenseNumber": "PH-002",
                "manager": "Sara Khan",
                "established": 2018,
            },
            {
                "_id": ObjectId(),
                "name": "Quick Meds — Karachi",
                "address": "789 Defence Road",
                "city": "Karachi",
                "phone": "021-9876543",
                "email": "karachi@quickmeds.pk",
                "licenseNumber": "PH-003",
                "manager": "Hassan Ali",
                "established": 2016,
            },
        ]
        db.pharmacies.insert_many(pharmacies)
        db.pharmacies.create_index("city")
        
        pha_ids = {p["name"]: p["_id"] for p in pharmacies}
        
        # ========================
        # 4. PERSONS (Patients, Doctors, Pharmacists)
        # ========================
        print("  ✓ Setting up Persons...")
        persons = [
            {
                "_id": ObjectId(),
                "name": "Dr. Ahmad Hassan",
                "roles": ["Doctor"],
                "specialization": "General Practitioner",
                "contactNumber": "0300-1234567",
                "email": "ahmad@clinic.pk",
                "address": "Medical Complex",
                "city": "Lahore",
                "licenseNumber": "DOC-001",
            },
            {
                "_id": ObjectId(),
                "name": "Dr. Fatima Khan",
                "roles": ["Doctor"],
                "specialization": "Cardiologist",
                "contactNumber": "0300-2345678",
                "email": "fatima@heart.pk",
                "address": "Heart Hospital",
                "city": "Islamabad",
                "licenseNumber": "DOC-002",
            },
            {
                "_id": ObjectId(),
                "name": "Muhammad Ali",
                "roles": ["Patient"],
                "contactNumber": "0321-1111111",
                "email": "ali@email.pk",
                "address": "House #5 Street 1",
                "city": "Lahore",
                "dateOfBirth": "1980-05-15",
            },
            {
                "_id": ObjectId(),
                "name": "Ayesha Ahmed",
                "roles": ["Patient"],
                "contactNumber": "0321-2222222",
                "email": "ayesha@email.pk",
                "address": "Apartment 10 Block B",
                "city": "Islamabad",
                "dateOfBirth": "1990-08-22",
            },
            {
                "_id": ObjectId(),
                "name": "Rashid Khan",
                "roles": ["Pharmacist"],
                "contactNumber": "0300-3333333",
                "email": "rashid@medlife.pk",
                "address": "MedLife Staff",
                "city": "Lahore",
                "licenseNumber": "PHARM-001",
            },
        ]
        db.persons.insert_many(persons)
        db.persons.create_index("roles")
        
        person_ids = {p["name"]: p["_id"] for p in persons}
        
        # ========================
        # 5. SUPPLIERS
        # ========================
        print("  ✓ Setting up Suppliers...")
        suppliers = [
            {
                "_id": ObjectId(),
                "companyName": "Global Pharma Inc",
                "contactPerson": "John Smith",
                "phone": "+1-555-0001",
                "email": "sales@globalpharma.com",
                "address": "New York, USA",
                "rating": 4.8,
                "paymentTerms": "Net 30",
            },
            {
                "_id": ObjectId(),
                "companyName": "Asia Medical Supplies",
                "contactPerson": "Chen Wei",
                "phone": "+86-10-1234567",
                "email": "sales@asiamedical.cn",
                "address": "Beijing, China",
                "rating": 4.5,
                "paymentTerms": "Net 45",
            },
            {
                "_id": ObjectId(),
                "companyName": "European Pharma Group",
                "contactPerson": "Marie Dubois",
                "phone": "+33-1-23456789",
                "email": "sales@eurpharma.fr",
                "address": "Paris, France",
                "rating": 4.7,
                "paymentTerms": "Net 60",
            },
        ]
        db.suppliers.insert_many(suppliers)
        db.suppliers.create_index("companyName")
        
        supplier_ids = {s["companyName"]: s["_id"] for s in suppliers}
        
        # ========================
        # 6. INVENTORY
        # ========================
        print("  ✓ Setting up Inventory...")
        inventory_docs = []
        for med in medicines:
            for pha in pharmacies:
                inventory_docs.append({
                    "_id": ObjectId(),
                    "medicineId": med["_id"],
                    "pharmacyId": pha["_id"],
                    "currentStock": 150,
                    "minimumThreshold": 50,
                    "batches": [
                        {
                            "batchNumber": f"BATCH-{med['name'][:5]}-001",
                            "manufacturingDate": datetime.now() - timedelta(days=30),
                            "expiryDate": datetime.now() + timedelta(days=330),
                            "quantityInBatch": 150,
                        }
                    ],
                    "lastRestocked": datetime.now(),
                    "warehouseLocation": f"Shelf-{chr(65 + (med['_id'].binary.hex()[0:2], 16)[0] % 26)}",
                })
        db.inventory.insert_many(inventory_docs)
        db.inventory.create_index([("medicineId", 1), ("pharmacyId", 1)])
        
        # ========================
        # 7. SUPPLY ORDERS
        # ========================
        print("  ✓ Setting up Supply Orders...")
        supply_orders = [
            {
                "_id": ObjectId(),
                "supplierId": supplier_ids["Global Pharma Inc"],
                "pharmacyId": pha_ids["MedLife Pharmacy — Lahore"],
                "medicineId": med_ids["Amoxicillin 500mg"],
                "quantityOrdered": 500,
                "unitCost": 400.00,
                "totalCost": 200000.00,
                "orderDate": datetime.now() - timedelta(days=5),
                "deliveryDate": datetime.now() + timedelta(days=2),
                "status": "Pending",
                "deliveryAddress": "123 Mall Road, Lahore",
            },
            {
                "_id": ObjectId(),
                "supplierId": supplier_ids["Asia Medical Supplies"],
                "pharmacyId": pha_ids["Health Center — Islamabad"],
                "medicineId": med_ids["Paracetamol 500mg"],
                "quantityOrdered": 1000,
                "unitCost": 20.00,
                "totalCost": 20000.00,
                "orderDate": datetime.now() - timedelta(days=10),
                "deliveryDate": datetime.now() - timedelta(days=2),
                "status": "Delivered",
                "deliveryAddress": "456 F-7, Islamabad",
            },
        ]
        db.supplyOrders.insert_many(supply_orders)
        db.supplyOrders.create_index("status")
        
        # ========================
        # 8. PRESCRIPTIONS
        # ========================
        print("  ✓ Setting up Prescriptions...")
        prescriptions = [
            {
                "_id": ObjectId(),
                "patientId": person_ids["Muhammad Ali"],
                "doctorId": person_ids["Dr. Ahmad Hassan"],
                "medicineId": med_ids["Amoxicillin 500mg"],
                "pharmacyId": pha_ids["MedLife Pharmacy — Lahore"],
                "prescriptionDate": datetime.now() - timedelta(days=2),
                "quantityPrescribed": 3,
                "dosage": "1 tablet twice daily",
                "duration": "7 days",
                "status": "Pending",
                "isControlledSubstance": False,
            },
            {
                "_id": ObjectId(),
                "patientId": person_ids["Ayesha Ahmed"],
                "doctorId": person_ids["Dr. Fatima Khan"],
                "medicineId": med_ids["Paracetamol 500mg"],
                "pharmacyId": pha_ids["Health Center — Islamabad"],
                "prescriptionDate": datetime.now() - timedelta(days=1),
                "quantityPrescribed": 10,
                "dosage": "1 tablet as needed",
                "duration": "15 days",
                "status": "Dispensed",
                "isControlledSubstance": False,
                "dispensedAt": datetime.now(),
            },
        ]
        db.prescriptions.insert_many(prescriptions)
        db.prescriptions.create_index([("patientId", 1)])
        db.prescriptions.create_index([("status", 1)])
        
        # ========================
        # CREATE INDEXES
        # ========================
        print("  ✓ Creating database indexes...")
        
        # Full-text search indexes
        db.medicines.create_index([("name", "text"), ("genericName", "text")])
        db.pharmacies.create_index([("name", "text"), ("address", "text")])
        db.persons.create_index([("name", "text")])
        
        # TTL index for old supply orders (expire after 1 year)
        db.supplyOrders.create_index(
            [("orderDate", 1)],
            expireAfterSeconds=365*24*60*60
        )
        
        # Compound indexes for common queries
        db.prescriptions.create_index([("patientId", 1), ("prescriptionDate", -1)])
        db.inventory.create_index([("currentStock", 1), ("minimumThreshold", 1)])
        
        # ========================
        # DISPLAY SUMMARY
        # ========================
        print("\n" + "=" * 60)
        print("DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print(f"\n📊 Summary:")
        print(f"  • Categories: {db.categories.count_documents({})}")
        print(f"  • Medicines: {db.medicines.count_documents({})}")
        print(f"  • Pharmacies: {db.pharmacies.count_documents({})}")
        print(f"  • Persons: {db.persons.count_documents({})}")
        print(f"  • Suppliers: {db.suppliers.count_documents({})}")
        print(f"  • Inventory: {db.inventory.count_documents({})}")
        print(f"  • Supply Orders: {db.supplyOrders.count_documents({})}")
        print(f"  • Prescriptions: {db.prescriptions.count_documents({})}")
        
        print(f"\n✓ Database URL: mongodb://localhost:27017/pharmacy_db")
        print(f"✓ Collections: {len(db.list_collection_names())}")
        print(f"\nYou can now run: python main.py\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nMake sure MongoDB is running on localhost:27017")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
