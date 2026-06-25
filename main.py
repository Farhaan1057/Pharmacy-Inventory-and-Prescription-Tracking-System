#!/usr/bin/env python3
"""
============================================================
PHARMACY CHAIN INVENTORY & PRESCRIPTION MANAGEMENT SYSTEM
CSC316 - Advance Database Systems - Terminal Project
Spring 2026 | COMSATS University Islamabad
============================================================
Run this file to start the application:
    python main.py

First-time setup:
    python -m database.setup_database

Requirements:
    pip install pymongo matplotlib pillow
    MongoDB must be running on localhost:27017
============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

# ============================================================
# DEPENDENCY CHECK & AUTO-INSTALL
# ============================================================
def check_dependencies():
    """Check and install missing dependencies."""
    required = ["pymongo", "matplotlib", "PIL"]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        install = {"PIL": "pillow"}
        for pkg in missing:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    install.get(pkg, pkg), "--break-system-packages", "-q"
                ])
                print(f"  ✓ Installed {pkg}")
            except Exception as e:
                print(f"  ✗ Failed to install {pkg}: {e}")
                return False
    
    return True


# Check dependencies before importing
if not check_dependencies():
    print("Failed to install dependencies. Exiting.")
    sys.exit(1)

# ============================================================
# IMPORTS
# ============================================================
from datetime import datetime
from database.connection import DatabaseConnection, COLORS, FONTS
from gui.dashboard import DashboardPage
from gui.medicines import MedicinesPage
from gui.inventory import InventoryPage
from gui.generic import (
    PrescriptionsPage, PharmaciesPage, PersonsPage, SuppliersPage, OrdersPage,
    AnalyticsPage, QueryLabPage, IndexesPage, OptimizationPage,
    BackupRestorePage, TransactionPrescriptionPage
)
from gui.settings import Sidebar, StatusBar


# ============================================================
# MAIN APPLICATION WINDOW
# ============================================================
class PharmacyApplication(tk.Tk):
    """Main application window for Pharmacy Management System."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("MedLife Pharmacy System - Advanced Database Management")
        self.geometry("1600x900")
        self.minsize(1400, 700)
        self.configure(bg=COLORS["bg_dark"])
        
        # Initialize database connection
        try:
            self.db = DatabaseConnection.get_db()
            print("✓ Connected to MongoDB")
        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                f"Cannot connect to MongoDB:\n{str(e)}\n\n"
                "Make sure MongoDB is running on localhost:27017"
            )
            self.destroy()
            return
        
        # Build UI
        self._build_ui()
        
        # Show dashboard on startup
        self.show_page("dashboard")
    
    def _build_ui(self):
        """Build the main UI with sidebar and content area."""
        
        # Main container
        main_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        main_frame.pack(fill="both", expand=True)
        
        # Left sidebar
        self.sidebar = Sidebar(main_frame, self.show_page)
        self.sidebar.pack(side="left", fill="y")
        
        # Right content area
        content_frame = tk.Frame(main_frame, bg=COLORS["bg_dark"])
        content_frame.pack(side="right", fill="both", expand=True)
        
        # Page container (for switching pages)
        self.page_container = tk.Frame(content_frame, bg=COLORS["bg_dark"])
        self.page_container.pack(fill="both", expand=True)
        
        # Status bar
        StatusBar(content_frame).pack(fill="x", side="bottom")
        
        # Page registry
        self.pages = {
            "dashboard": self._create_page(DashboardPage),
            "medicines": self._create_page(MedicinesPage),
            "inventory": self._create_page(InventoryPage),
            "prescriptions": self._create_page(PrescriptionsPage),
            "pharmacies": self._create_page(PharmaciesPage),
            "persons": self._create_page(PersonsPage),
            "suppliers": self._create_page(SuppliersPage),
            "orders": self._create_page(OrdersPage),
            "analytics": self._create_page(AnalyticsPage),
            "querylab": self._create_page(QueryLabPage),
            "indexes": self._create_page(IndexesPage),
            "optimization": self._create_page(OptimizationPage),
            "backup": self._create_page(BackupRestorePage),
            "transactions": self._create_page(TransactionPrescriptionPage),
        }
    
    def _create_page(self, PageClass):
        """Create a page instance."""
        def create():
            return PageClass(self.page_container, self.db)
        return create
    
    def show_page(self, page_name):
        """Switch to a specific page."""
        
        # Validate page exists
        if page_name not in self.pages:
            messagebox.showwarning("Page Not Found", f"Page '{page_name}' not found.")
            return
        
        # Clear container
        for widget in self.page_container.winfo_children():
            widget.destroy()
        
        # Create and display new page
        try:
            page = self.pages[page_name]()
            page.pack(fill="both", expand=True)
        except Exception as e:
            error_frame = tk.Frame(self.page_container, bg=COLORS["bg_dark"])
            error_frame.pack(fill="both", expand=True)
            
            tk.Label(error_frame,
                     text=f"Error loading page: {str(e)}",
                     font=FONTS["title"],
                     fg=COLORS["danger"],
                     bg=COLORS["bg_dark"]).pack(expand=True)
            
            print(f"ERROR: Failed to load page '{page_name}':\n{str(e)}")


# ============================================================
# ENTRY POINT
# ============================================================
def main():
    """Application entry point."""
    
    print("\n" + "=" * 60)
    print("PHARMACY CHAIN INVENTORY & PRESCRIPTION MANAGEMENT SYSTEM")
    print("CSC316 - Advance Database Systems")
    print("COMSATS University Islamabad - Spring 2026")
    print("=" * 60 + "\n")
    
    print("Starting application...")
    print("→ Python", sys.version.split()[0])
    print("→ Tkinter version", tk.TkVersion)
    
    # Create and run application
    app = PharmacyApplication()
    
    if app.winfo_exists():
        app.mainloop()
    
    print("\n✓ Application closed")


if __name__ == "__main__":
    main()