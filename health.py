"""
Health Check & Production Diagnostics Module.
Provides readiness and liveness verification for production orchestration (Docker, K8s).
Conforms to IEEE Std 730/12207 standards.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict

from config import CONFIG
from storage import DatabaseManager, StorageEngine


def perform_health_check() -> Dict[str, Any]:
    """Execute complete diagnostic suite on database, storage, and filesystem."""
    status = "healthy"
    details: Dict[str, Any] = {}

    # 1. Database Connectivity & WAL verification
    try:
        conn = DatabaseManager.get_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tasks;")
        task_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM sessions;")
        session_count = cur.fetchone()[0]

        details["database"] = {
            "backend": StorageEngine.get_active_backend(),
            "status": "connected",
            "journal_mode": journal_mode,
            "tasks_count": task_count,
            "sessions_count": session_count,
        }
    except Exception as e:
        status = "degraded"
        details["database"] = {"status": "error", "error": str(e)}

    # 2. Filesystem write permissions
    try:
        test_file = CONFIG.data_dir / ".health_check.tmp"
        test_file.write_text("health", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        details["filesystem"] = {"status": "writable", "path": str(CONFIG.data_dir)}
    except Exception as e:
        status = "degraded"
        details["filesystem"] = {"status": "read_only_error", "error": str(e)}

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": CONFIG.env,
        "details": details,
    }
