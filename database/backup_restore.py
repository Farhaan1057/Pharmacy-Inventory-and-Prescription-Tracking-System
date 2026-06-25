"""
database/backup_restore.py
==========================
Helpers for running mongodump and mongorestore as subprocesses.
Used by gui/backup.py.
"""

import os
import subprocess
import threading
from datetime import datetime


class BackupRestoreHelper:
    """
    Wraps mongodump / mongorestore commands.

    Usage:
        helper = BackupRestoreHelper()
        helper.backup(
            db_name="pharmacy_db",
            out_dir="./PharmacyBackup",
            log_callback=lambda line: print(line)
        )
    """

    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = "27017"

    # ── BACKUP ───────────────────────────────────────────────
    def backup(self, db_name: str, out_dir: str,
               log_callback=None, done_callback=None):
        """
        Run mongodump in a background thread.
        log_callback(line)  called for each output line.
        done_callback(success: bool)  called when finished.
        """
        cmd = [
            "mongodump",
            "--host", self.DEFAULT_HOST,
            "--port", self.DEFAULT_PORT,
            "--db",   db_name,
            "--out",  out_dir,
        ]
        self._run_async(cmd, "BACKUP", log_callback, done_callback)

    # ── RESTORE ──────────────────────────────────────────────
    def restore(self, db_name: str, src_dir: str,
                drop: bool = True,
                log_callback=None, done_callback=None):
        """
        Run mongorestore in a background thread.
        src_dir should point to the directory that contains the db folder,
        e.g. "./PharmacyBackup"  (mongorestore will find pharmacy_db/ inside).
        """
        target = os.path.join(src_dir, db_name)
        cmd = [
            "mongorestore",
            "--host", self.DEFAULT_HOST,
            "--port", self.DEFAULT_PORT,
            "--db",   db_name,
            target,
        ]
        if drop:
            cmd.insert(1, "--drop")
        self._run_async(cmd, "RESTORE", log_callback, done_callback)

    # ── INTERNAL ─────────────────────────────────────────────
    def _run_async(self, cmd: list, label: str,
                   log_callback, done_callback):
        def _worker():
            _log = log_callback or (lambda l: None)
            _log(f"{'='*50}")
            _log(f"  {label} STARTED  {datetime.now().strftime('%H:%M:%S')}")
            _log(f"  Command: {' '.join(cmd)}")
            _log(f"{'='*50}")
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True)
                for line in proc.stdout:
                    _log(line.rstrip())
                proc.wait()
                success = proc.returncode == 0
                if success:
                    _log(f"\n✅  {label} COMPLETED SUCCESSFULLY")
                else:
                    _log(f"\n❌  {label} FAILED  (exit code {proc.returncode})")
                if done_callback:
                    done_callback(success)
            except FileNotFoundError:
                _log(f"\n❌  '{cmd[0]}' not found.\n"
                     "    Install MongoDB Database Tools and add to PATH.\n"
                     "    https://www.mongodb.com/try/download/database-tools")
                if done_callback:
                    done_callback(False)

        threading.Thread(target=_worker, daemon=True).start()

    # ── UTILITY ──────────────────────────────────────────────
    @staticmethod
    def is_mongodump_available() -> bool:
        """Check if mongodump is installed and on PATH."""
        try:
            subprocess.run(["mongodump", "--version"],
                           capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False