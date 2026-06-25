"""
database/connection.py
======================
MongoDB connection singleton.
Also defines the shared COLORS and FONTS used across all GUI modules.
"""

import subprocess, sys

# ── auto-install pymongo if missing ──────────────────────────
def _ensure_pymongo():
    try:
        import pymongo  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pymongo",
             "--break-system-packages", "-q"])

_ensure_pymongo()

from pymongo import MongoClient


# ============================================================
# DATABASE CONNECTION
# ============================================================
class DatabaseConnection:
    _instance = None

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            try:
                cls._instance = MongoClient(
                    "mongodb://localhost:27017/",
                    serverSelectionTimeoutMS=3000)
                cls._instance.server_info()
            except Exception as e:
                raise ConnectionError(
                    f"Cannot connect to MongoDB on localhost:27017\n\n"
                    f"Error: {e}\n\nMake sure MongoDB is running.")
        return cls._instance

    @classmethod
    def get_db(cls):
        return cls.get_client()["pharmacy_db"]


# ============================================================
# SHARED THEME  (imported by every GUI module)
# ============================================================
COLORS = {
    "bg_dark":       "#0D1117",
    "bg_card":       "#161B22",
    "bg_sidebar":    "#0D1117",
    "accent":        "#2C6E49",
    "accent_light":  "#40916C",
    "accent_hover":  "#52B788",
    "text_primary":  "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":    "#484F58",
    "border":        "#30363D",
    "danger":        "#F85149",
    "warning":       "#E3B341",
    "success":       "#3FB950",
    "info":          "#58A6FF",
    "white":         "#FFFFFF",
    "btn_text":      "#FFFFFF",
}

FONTS = {
    "title":   ("Segoe UI", 18, "bold"),
    "heading": ("Segoe UI", 13, "bold"),
    "subhead": ("Segoe UI", 11, "bold"),
    "body":    ("Segoe UI", 10),
    "small":   ("Segoe UI", 9),
    "code":    ("Consolas", 9),
    "nav":     ("Segoe UI", 10, "bold"),
}