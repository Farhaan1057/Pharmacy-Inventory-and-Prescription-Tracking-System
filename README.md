# 💊 MedLife Pharmacy Inventory & Prescription Management System

## Project Overview

A comprehensive **desktop application** for managing pharmacy chain inventory, prescriptions, suppliers, and multi-location pharmacies. Built with **Python Tkinter** GUI and **MongoDB** database backend.

### Key Features

- ✅ **Medicine Registry** - Add, edit, delete, search medicines
- ✅ **Inventory Management** - Track stock levels across branches, low-stock alerts
- ✅ **Prescription Tracking** - Manage prescriptions, dispensing, patient records
- ✅ **Multi-Branch Support** - Support for multiple pharmacy locations
- ✅ **Analytics Dashboard** - Charts, trends, performance metrics
- ✅ **Advanced Queries** - MongoDB aggregation pipeline interface
- ✅ **Database Optimization** - Indexes, query analysis
- ✅ **Backup & Restore** - Database backup/restore operations
- ✅ **ACID Transactions** - Atomic prescription dispensing (MongoDB)

---

## Project Structure

```
Pharmacy System/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── database/
│   ├── __init__.py                 # Database package initialization
│   ├── connection.py               # MongoDB connection singleton
│   ├── crud.py                     # CRUD helper functions
│   ├── aggregations.py             # MongoDB aggregation pipelines
│   ├── indexes.py                  # Index management utilities
│   ├── transactions.py             # ACID transaction helpers
│   ├── backup_restore.py           # Backup and restore operations
│   └── setup_database.py           # Database initialization script
├── gui/
│   ├── __init__.py                 # GUI package initialization
│   ├── main.py                     # Main app window (legacy)
│   ├── dashboard.py                # Dashboard page
│   ├── settings.py                 # Shared UI components
│   ├── medicines.py                # Medicines management page
│   ├── inventory.py                # Inventory management page
│   ├── generic.py                  # Generic pages (Prescriptions, etc.)
│   └── [other page modules]
├── docs/                           # Documentation (if any)
└── assets/                         # Images, icons (if any)
```

---

## Installation & Setup

### 1. Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **MongoDB Community Edition** ([Download](https://www.mongodb.com/try/download/community))
  - Must be running on `localhost:27017`
  - Default database: `pharmacy_db`

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Or manually:
pip install pymongo matplotlib pillow reportlab
```

### 3. Initialize Database

```bash
# First time setup - creates collections and sample data
python -m database.setup_database
```

This will:
- Create 8 collections: medicines, pharmacies, persons, prescriptions, suppliers, etc.
- Add sample data for testing
- Create optimized indexes
- Display summary

### 4. Run Application

```bash
# Start the application
python main.py
```

The application window will open with the Dashboard page.

---

## Usage Guide

### Main Navigation

Use the **left sidebar** to navigate between pages:

#### 🔷 Overview
- **Dashboard** - System statistics, stock levels, alerts

#### 🔷 Management
- **Medicines** - Browse, search, add/edit medicines
- **Inventory** - Track stock, low-stock alerts, near-expiry items
- **Pharmacies** - Branch locations and details
- **Persons** - Patients, doctors, pharmacists database
- **Prescriptions** - Create, track, dispense prescriptions
- **Supply Orders** - Supplier orders and delivery tracking
- **Suppliers** - Supplier information and ratings

#### 🔷 Analytics
- **Analytics** - Visual charts and reports
- **Query Lab** - Custom MongoDB aggregation queries

#### 🔷 Database
- **Indexes** - Create and manage database indexes
- **Optimization** - Database statistics and tips
- **Backup/Restore** - Backup and restore operations
- **Transactions** - ACID transaction testing

### Key Operations

#### Adding a Medicine
1. Go to **Medicines** tab
2. Click **+ Add Medicine** button
3. Fill in details: name, generic name, price, category, etc.
4. Click **Save Medicine**

#### Managing Inventory
1. Go to **Inventory** tab
2. View current stock levels
3. Use **Adjust Stock** to update quantities
4. Filter by "Low Stock Only" or "Near Expiry"

#### Creating Prescriptions
1. Go to **Prescriptions** tab
2. Click **+ New Rx**
3. Select patient, doctor, medicine, and pharmacy
4. Click **Create Prescription**

#### Running Custom Queries
1. Go to **Query Lab**
2. Write MongoDB aggregation pipeline (JSON format)
3. Select collection to query
4. Click **Execute** to see results

---

## Database Schema

### Collections

#### 1. **medicines**
```json
{
  "_id": ObjectId(),
  "name": "Amoxicillin 500mg",
  "genericName": "Amoxicillin",
  "manufacturer": "Pharma Ltd",
  "type": "PrescriptionMedicine",  // or "OTCMedicine"
  "categoryId": ObjectId(),
  "unitPrice": 450.00,
  "minimumStockThreshold": 50,
  "strength": "500mg",
  "requiresPrescription": true,
  "controlledSubstance": false
}
```

#### 2. **pharmacies**
```json
{
  "_id": ObjectId(),
  "name": "MedLife Pharmacy — Lahore",
  "address": "123 Mall Road",
  "city": "Lahore",
  "phone": "042-1234567",
  "email": "lahore@medlife.pk",
  "licenseNumber": "PH-001",
  "manager": "Ali Ahmed",
  "established": 2015
}
```

#### 3. **prescriptions**
```json
{
  "_id": ObjectId(),
  "patientId": ObjectId(),
  "doctorId": ObjectId(),
  "medicineId": ObjectId(),
  "pharmacyId": ObjectId(),
  "prescriptionDate": ISODate(),
  "quantityPrescribed": 3,
  "dosage": "1 tablet twice daily",
  "duration": "7 days",
  "status": "Pending",  // or "Dispensed", "Expired", "Cancelled"
  "isControlledSubstance": false,
  "dispensedAt": ISODate()
}
```

#### 4. **inventory**
```json
{
  "_id": ObjectId(),
  "medicineId": ObjectId(),
  "pharmacyId": ObjectId(),
  "currentStock": 150,
  "minimumThreshold": 50,
  "batches": [
    {
      "batchNumber": "BATCH-AMX-001",
      "manufacturingDate": ISODate(),
      "expiryDate": ISODate(),
      "quantityInBatch": 150
    }
  ],
  "lastRestocked": ISODate()
}
```

#### 5. **persons** (Patients, Doctors, Pharmacists)
```json
{
  "_id": ObjectId(),
  "name": "Dr. Ahmad Hassan",
  "roles": ["Doctor"],
  "specialization": "General Practitioner",
  "contactNumber": "0300-1234567",
  "email": "ahmad@clinic.pk",
  "address": "Medical Complex",
  "city": "Lahore",
  "licenseNumber": "DOC-001"
}
```

#### 6. **supplyOrders**
```json
{
  "_id": ObjectId(),
  "supplierId": ObjectId(),
  "pharmacyId": ObjectId(),
  "medicineId": ObjectId(),
  "quantityOrdered": 500,
  "unitCost": 400.00,
  "totalCost": 200000.00,
  "orderDate": ISODate(),
  "deliveryDate": ISODate(),
  "status": "Pending",  // or "Delivered"
  "deliveryAddress": "123 Mall Road, Lahore"
}
```

#### 7. **suppliers**
```json
{
  "_id": ObjectId(),
  "companyName": "Global Pharma Inc",
  "contactPerson": "John Smith",
  "phone": "+1-555-0001",
  "email": "sales@globalpharma.com",
  "address": "New York, USA",
  "rating": 4.8,
  "paymentTerms": "Net 30"
}
```

#### 8. **categories**
```json
{
  "_id": ObjectId(),
  "name": "Antibiotics",
  "description": "Antibiotic medicines"
}
```

---

## Advanced Features

### 1. MongoDB Aggregation Pipelines

The system includes 12+ pre-built aggregation pipelines:
- Top prescribed medicines
- Prescriptions per doctor
- Stock level per branch
- Supplier performance ranking
- Controlled substance flags
- Revenue per pharmacy
- And more...

### 2. Indexing & Optimization

```python
# Single-field indexes
medicines.create_index("name")

# Compound indexes
prescriptions.create_index([("patientId", 1), ("prescriptionDate", -1)])

# Text search indexes
medicines.create_index([("name", "text"), ("genericName", "text")])

# TTL indexes (auto-expire old documents)
supplyOrders.create_index([("orderDate", 1)], expireAfterSeconds=31536000)
```

### 3. ACID Transactions

For prescription dispensing with guaranteed atomicity:

```python
# Dispense prescription atomically
session = db.client.start_session()
try:
    with session.start_transaction():
        # 1. Check stock
        # 2. Validate availability
        # 3. Decrement stock
        # 4. Mark prescription as dispensed
    print("Dispensing successful!")
except Exception as e:
    print(f"Transaction rolled back: {e}")
finally:
    session.end_session()
```

### 4. Backup & Restore

```bash
# Backup (automatic mongodump)
# Restore (automatic mongorestore)
# Both available in GUI: Database → Backup/Restore tab
```

---

## Troubleshooting

### Error: "Cannot connect to MongoDB"
- Verify MongoDB is running: `mongosh`
- Check connection: `mongodb://localhost:27017/`
- Restart MongoDB service if needed

### Error: "Database not initialized"
- Run: `python -m database.setup_database`
- This creates all necessary collections and indexes

### Error: "Missing dependencies"
- Run: `pip install -r requirements.txt`
- Or: `pip install pymongo matplotlib pillow`

### Slow Queries
- Check indexes via **Database → Indexes** tab
- Use **Database → Optimization** for statistics
- Run custom queries in **Query Lab** to test

---

## Project Statistics

| Aspect | Count |
|--------|-------|
| Python Files | 12+ |
| GUI Pages | 14 |
| Database Collections | 8 |
| MongoDB Pipelines | 12+ |
| Indexes Managed | 15+ |
| Lines of Code | 3500+ |

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python 3.8+** | Backend & CLI |
| **Tkinter** | GUI Framework |
| **MongoDB** | NoSQL Database |
| **PyMongo** | MongoDB Driver |
| **Matplotlib** | Data Visualization |
| **Pillow** | Image Processing |

---

## Features Checklist

- [x] Medicine management (CRUD)
- [x] Inventory tracking
- [x] Prescription management
- [x] Multi-location support
- [x] Analytics dashboard
- [x] Custom query interface
- [x] Database indexing
- [x] Backup/Restore
- [x] ACID transactions
- [x] Alert system (low stock, near expiry)
- [x] Search & filtering
- [x] Pagination
- [x] Professional UI theme

---

## Future Enhancements

- [ ] User authentication & role-based access
- [ ] Email notifications for low stock
- [ ] Report generation (PDF/Excel)
- [ ] API backend (FastAPI/Flask)
- [ ] Mobile app companion
- [ ] Real-time inventory sync
- [ ] Advanced analytics (forecasting)
- [ ] Barcode scanning support

---

## Team & Credits

**CSC316: Advanced Database Systems**  
**Spring 2026 - COMSATS University Islamabad**

### Development
- Modern Tkinter GUI with Material Design
- MongoDB aggregation frameworks
- Advanced database optimization

### Database
- 8 normalized collections
- Multi-stage aggregation pipelines
- Compound indexing strategy
- ACID transaction support

---

## License

Educational Project - COMSATS University Islamabad

---

## Quick Start Commands

```bash
# Initial setup
python -m database.setup_database

# Run application
python main.py

# View MongoDB
mongosh  # or mongo shell

# Reset database
python -m database.setup_database  # Clears and recreates
```

---

For more information, see project documentation in `/docs` or contact the development team.

**Happy Pharmacies Management! 💊**
