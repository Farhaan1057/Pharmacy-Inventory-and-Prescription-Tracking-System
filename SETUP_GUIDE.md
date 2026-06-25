# 🚀 MedLife Pharmacy System - Complete Setup Guide

## Step-by-Step Installation

### Step 1: Prerequisites Installation

#### 1.1 Install Python 3.8 or Higher
- Download from [python.org](https://www.python.org/downloads/)
- Windows: Use installer, select "Add Python to PATH"
- macOS: Use homebrew or installer
- Linux: `sudo apt-get install python3 python3-pip`

Verify installation:
```bash
python --version   # Should show 3.8+
pip --version
```

#### 1.2 Install MongoDB Community Edition
- Download from [mongodb.com](https://www.mongodb.com/try/download/community)
- Windows: Run MSI installer, select MongoDB as service
- macOS: `brew tap mongodb/brew && brew install mongodb-community`
- Linux: Follow [official docs](https://docs.mongodb.com/manual/installation/)

Start MongoDB:
```bash
# Windows (Service): Automatic on startup
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# Test connection:
mongosh
> db.version()
> exit
```

### Step 2: Project Setup

#### 2.1 Create Project Directory
```bash
# Navigate to your workspace
cd Desktop  # or preferred location

# Create/enter project directory
mkdir "Pharmacy Project"
cd "Pharmacy Project"
```

#### 2.2 Install Python Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or manually:
pip install pymongo==4.3.0 matplotlib==3.6.2 pillow==9.4.0 reportlab==4.0.4
```

Verify installations:
```bash
python -c "import pymongo; import matplotlib; import PIL; print('✓ All dependencies installed')"
```

### Step 3: Database Initialization

#### 3.1 Initialize Database
```bash
# Run setup script
python -m database.setup_database
```

Expected output:
```
============================================================
PHARMACY INVENTORY & PRESCRIPTION SYSTEM - DATABASE SETUP
============================================================

✓ Connected to MongoDB: pharmacy_db
→ Clearing existing data...
→ Creating collections and indexes...
  ✓ Setting up Categories...
  ✓ Setting up Medicines...
  ✓ Setting up Pharmacies...
  [... more setup messages ...]

============================================================
DATABASE SETUP COMPLETED SUCCESSFULLY!
============================================================

📊 Summary:
  • Categories: 5
  • Medicines: 5
  • Pharmacies: 3
  • Persons: 5
  • Suppliers: 3
  • Inventory: 15
  • Supply Orders: 2
  • Prescriptions: 2

  + BULK DATA ADDED

✓ Database URL: mongodb://localhost:27017/pharmacy_db
✓ Collections: 8

You can now run: python main.py
```

#### 3.2 Verify Database
```bash
# Connect to MongoDB shell
mongosh

# Check database exists
show databases

# Switch to pharmacy_db
use pharmacy_db

# Check collections
show collections

# Count documents in medicines
db.medicines.countDocuments()
# Should return: 5

# Exit
exit
```

### Step 4: Run Application

#### 4.1 Start Application
```bash
python main.py
```

Expected output:
```
============================================================
PHARMACY CHAIN INVENTORY & PRESCRIPTION MANAGEMENT SYSTEM
CSC316 - Advance Database Systems
COMSATS University Islamabad - Spring 2026
============================================================

Starting application...
→ Python 3.10.0
→ Tkinter version 8.6
✓ Connected to MongoDB
```

The GUI window will open with the Dashboard page.

#### 4.2 First Time Usage
1. **Dashboard** - View system overview and statistics
2. **Medicines** - See 5 sample medicines
3. **Inventory** - Check stock levels
4. **Pharmacies** - View 3 branch locations
5. **Prescriptions** - Create sample prescriptions

---

## File Structure Overview

```
ProjectRoot/
├── main.py                      ← Start here (python main.py)
├── requirements.txt             ← Dependencies
├── README.md                    ← Project documentation
├── SETUP_GUIDE.md              ← This file
│
├── database/
│   ├── __init__.py
│   ├── connection.py           ← MongoDB connection
│   ├── setup_database.py       ← Database initialization
│   ├── crud.py                 ← CRUD operations
│   ├── aggregations.py         ← 12+ aggregation pipelines
│   ├── indexes.py              ← Index management
│   ├── transactions.py         ← ACID transactions
│   └── backup_restore.py       ← Backup/restore operations
│
└── gui/
    ├── __init__.py
    ├── dashboard.py            ← Dashboard page
    ├── settings.py             ← Shared UI components
    ├── medicines.py            ← Medicine management
    ├── inventory.py            ← Inventory management
    └── generic.py              ← All other pages
```

---

## Common Issues & Solutions

### Issue 1: "Cannot connect to MongoDB"

**Problem**: Error when starting application
```
ConnectionError: Cannot connect to MongoDB on localhost:27017
```

**Solution**:
1. Verify MongoDB is running:
   ```bash
   mongosh  # Should connect without error
   ```
2. If not running, start it:
   - **Windows**: Check Services → MongoDB → Start
   - **macOS**: `brew services start mongodb-community`
   - **Linux**: `sudo systemctl start mongod`
3. Verify default port (27017) is not blocked

### Issue 2: "Database not initialized"

**Problem**: Application runs but shows no data

**Solution**:
```bash
# Re-run database setup
python -m database.setup_database

# Verify in MongoDB shell
mongosh
> use pharmacy_db
> db.medicines.countDocuments()  # Should show 5
```

### Issue 3: "No module named 'pymongo'"

**Problem**: Import error for pymongo

**Solution**:
```bash
# Reinstall pymongo
pip uninstall pymongo
pip install pymongo

# Or install all dependencies fresh
pip install -r requirements.txt
```

### Issue 4: "Tkinter not found"

**Problem**: `_tkinter.TclError` or Tkinter import error

**Solution**:
- **Windows**: Python installer should include Tkinter
- **macOS**: `brew install python-tk`
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`

### Issue 5: Slow Performance

**Problem**: Application is slow or queries timeout

**Solution**:
1. Check MongoDB is running efficiently:
   ```bash
   mongosh
   > db.serverStatus()  # Check memory usage
   ```
2. Create missing indexes:
   - Go to **Database → Indexes** tab
   - Review and create recommended indexes
3. Archive old data:
   - Delete old prescriptions/orders from MongoDB shell

---

## Database Verification Checklist

After setup, verify:

```bash
mongosh
> use pharmacy_db
> db.medicines.countDocuments()          # Should be 5
> db.pharmacies.countDocuments()         # Should be 3
> db.persons.countDocuments()            # Should be 5
> db.prescriptions.countDocuments()      # Should be 2
> db.inventory.countDocuments()          # Should be 15
> db.supplyOrders.countDocuments()       # Should be 2
> db.suppliers.countDocuments()          # Should be 3
> db.categories.countDocuments()         # Should be 5
> exit
```

---

## Development & Customization

### Adding a Custom Medicine

Via GUI:
1. Click **Medicines** in sidebar
2. Click **+ Add Medicine**
3. Fill form and click **Save Medicine**

Via MongoDB:
```bash
mongosh
> use pharmacy_db
> db.medicines.insertOne({
    name: "Custom Drug",
    genericName: "CustomGeneric",
    manufacturer: "Pharma Inc",
    type: "PrescriptionMedicine",
    unitPrice: 500,
    minimumStockThreshold: 25,
    strength: "100mg",
    requiresPrescription: true,
    controlledSubstance: false
  })
```

### Running Custom MongoDB Queries

1. Go to **Analytics → Query Lab**
2. Write aggregation pipeline:
```json
[
  {"$match": {"status": "Pending"}},
  {"$group": {"_id": "$pharmacyId", "count": {"$sum": 1}}},
  {"$sort": {"count": -1}}
]
```
3. Select collection: `prescriptions`
4. Click **Execute**

### Creating Database Backups

```bash
# Via GUI: Database → Backup/Restore → Create Backup

# Or manually:
mongodump --db pharmacy_db --out ./backups/

# Restore:
mongorestore --db pharmacy_db ./backups/pharmacy_db/
```

---

## Performance Tips

1. **Use Indexes**: Created by default, but add more for custom queries
2. **Pagination**: Tables show 15 items per page
3. **Search**: Use text search indexes for full-text search
4. **Batch Operations**: Combine multiple inserts/updates
5. **Archive Old Data**: Delete records older than 1 year

---

## Resetting the Database

To start fresh:

```bash
# Option 1: Using application
python -m database.setup_database
# This clears all data and recreates with samples

# Option 2: Using MongoDB shell
mongosh
> use pharmacy_db
> db.dropDatabase()  # Deletes entire database
# Then run: python -m database.setup_database
```

---

## Troubleshooting Checklist

- [ ] Python 3.8+ installed
- [ ] MongoDB running on localhost:27017
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database initialized: `python -m database.setup_database`
- [ ] MongoDB collections created: `mongosh → show collections`
- [ ] Sample data exists: `db.medicines.countDocuments()` shows 5
- [ ] Application starts: `python main.py`
- [ ] Dashboard loads with statistics
- [ ] Can navigate to different pages

---

## Getting Help

### View Logs
```bash
# Check MongoDB logs
# Windows: Check Event Viewer
# macOS: brew logs mongodb-community
# Linux: sudo journalctl -u mongod
```

### Test Connections
```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017/'))"

# Test database access
python -c "from database.connection import DatabaseConnection; db = DatabaseConnection.get_db(); print(db.medicines.count_documents({}))"
```

### Reset Everything
```bash
# 1. Uninstall and reinstall Python packages
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 2. Reset MongoDB database
mongosh
> use pharmacy_db
> db.dropDatabase()

# 3. Reinitialize
python -m database.setup_database

# 4. Start application
python main.py
```

---

## Next Steps

After successful setup:

1. **Explore the Dashboard** - See system overview
2. **Add Sample Data** - Create medicines, pharmacies, persons
3. **Create Prescriptions** - Understand workflow
4. **Run Analytics** - View charts and trends
5. **Write Custom Queries** - Use Query Lab for exploration
6. **Study Code** - Review implementation in `/database` and `/gui`

---

## System Requirements Summary

| Component | Requirement |
|-----------|------------|
| OS | Windows 10+, macOS 10.14+, Linux (any) |
| Python | 3.8 or higher |
| MongoDB | 4.4 or higher |
| RAM | 2 GB minimum, 4 GB recommended |
| Disk | 500 MB free space |
| Internet | For pip install only |

---

## Support & Contact

For issues or questions:
1. Check README.md for feature documentation
2. Review this SETUP_GUIDE.md
3. Check database logs
4. Review application console output

**Project**: CSC316 Advanced Database Systems  
**University**: COMSATS University Islamabad  
**Semester**: Spring 2026

---

**Happy Setup! 💊**  
If you encounter any issues, follow the Troubleshooting section above.
