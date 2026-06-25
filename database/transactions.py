"""
database/transactions.py
========================
MongoDB multi-document transaction logic.

REQUIREMENT: Transactions need a Replica Set.
On a standalone localhost mongod they are NOT supported.
TransactionHelper.dispense() detects this automatically and
raises a StandaloneError so the caller can fall back gracefully.
"""

from datetime import datetime


class StandaloneError(Exception):
    """Raised when transactions are attempted on a non-replica-set mongod."""
    pass


class TransactionHelper:
    """
    Wraps MongoDB session transactions for prescription dispense.

    Usage (in GUI):
        th = TransactionHelper(db, client)
        try:
            log = th.dispense(rx_id, med_id, pha_id, qty)
        except StandaloneError:
            # fall back to CRUDHelper.dispense_prescription()
            ...
        except ValueError as e:
            # insufficient stock — rollback already happened
            ...
    """

    def __init__(self, db, client):
        self.db     = db
        self.client = client

    def dispense(self, rx_id, medicine_id, pharmacy_id, qty: int) -> list:
        """
        Execute an ACID transaction to dispense a prescription item.

        Steps:
          1. Read inventory inside the session
          2. Validate stock >= qty  (abort if not)
          3. Decrement currentStock
          4. Set prescription.status = 'Dispensed'

        Returns a list of log strings describing each step.
        Raises StandaloneError if replica set is unavailable.
        Raises ValueError if stock is insufficient (after rollback).
        """
        log = []

        try:
            with self.client.start_session() as session:
                log.append(f"[TXN] Session started  {datetime.now().strftime('%H:%M:%S')}")
                with session.start_transaction():
                    log.append("[TXN] Transaction opened")

                    # Step 1 — Read inventory
                    inv = self.db.inventory.find_one(
                        {"medicineId": medicine_id, "pharmacyId": pharmacy_id},
                        session=session)
                    if not inv:
                        raise ValueError("No inventory record found for this medicine/pharmacy.")

                    current = inv.get("currentStock", 0)
                    log.append(f"[TXN] Current stock  : {current}")

                    # Step 2 — Stock check
                    if current < qty:
                        raise ValueError(
                            f"Insufficient stock — ROLLBACK\n"
                            f"    Available: {current}  |  Requested: {qty}")

                    # Step 3 — Decrement stock
                    self.db.inventory.update_one(
                        {"_id": inv["_id"]},
                        {"$inc": {"currentStock": -qty}},
                        session=session)
                    log.append(f"[TXN] Stock updated  : {current} → {current - qty}")

                    # Step 4 — Mark prescription Dispensed
                    self.db.prescriptions.update_one(
                        {"_id": rx_id},
                        {"$set": {
                            "status":      "Dispensed",
                            "dispensedAt": datetime.now()
                        }},
                        session=session)
                    log.append("[TXN] Prescription   : status → Dispensed")

                # Committed automatically on __exit__
                log.append("[TXN] ✅  COMMITTED")

        except Exception as e:
            err = str(e)
            # pymongo raises OperationFailure / InvalidOperation for standalone
            if any(k in err for k in ["replica", "Transaction", "not supported",
                                       "OperationFailure"]):
                raise StandaloneError(err)
            raise   # re-raise ValueError (stock) or anything else

        return log

    # ── Convenience: pipeline that shows the transaction steps ──
    @staticmethod
    def transaction_code_snippet() -> str:
        return '''\
# STEP 2 — MongoDB Multi-Document Transaction Pattern
# Requires: Replica Set  (e.g. Atlas or local rs.initiate())

with client.start_session() as session:
    with session.start_transaction():
        try:
            # 1. Check stock (inside session)
            inv = db.inventory.find_one(
                {"medicineId": med_id, "pharmacyId": pha_id},
                session=session
            )
            if inv["currentStock"] < qty:
                raise ValueError("Insufficient stock — ROLLBACK")

            # 2. Decrement stock
            db.inventory.update_one(
                {"_id": inv["_id"]},
                {"$inc": {"currentStock": -qty}},
                session=session
            )

            # 3. Mark prescription Dispensed
            db.prescriptions.update_one(
                {"_id": rx_id},
                {"$set": {"status": "Dispensed",
                          "dispensedAt": datetime.now()}},
                session=session
            )
            # Commit happens automatically on __exit__

        except Exception:
            session.abort_transaction()   # ROLLBACK
            raise
'''