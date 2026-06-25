"""
gui package — all page classes for MedLife Pharmacy System
"""
from gui.dashboard       import DashboardPage
from gui.inventory       import InventoryPage, MedicinesPage
from gui.medicines       import MedicinesPage as MedicinesPageExtended
from gui.generic         import (
    PrescriptionsPage, PharmaciesPage, PersonsPage, SuppliersPage, OrdersPage,
    AnalyticsPage, QueryLabPage, IndexesPage, OptimizationPage,
    BackupRestorePage, TransactionPrescriptionPage
)
from gui.settings        import Sidebar, StatusBar, Card, AccentButton, DataTable, SectionTitle

__all__ = [
    "DashboardPage",
    "InventoryPage", "MedicinesPage", "MedicinesPageExtended",
    "PrescriptionsPage", "PharmaciesPage", "PersonsPage", "SuppliersPage", "OrdersPage",
    "AnalyticsPage", "QueryLabPage",
    "IndexesPage", "OptimizationPage",
    "BackupRestorePage", "TransactionPrescriptionPage",
    "Sidebar", "StatusBar",
    "Card", "AccentButton", "DataTable", "SectionTitle",
]