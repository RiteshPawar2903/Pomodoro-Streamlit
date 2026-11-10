"""
Configuration module for Zen Pomodoro Clock.
Follows IEEE Std 828 / 12207 configuration management and environment isolation standards.
Supports zero-hardcoded configuration with seamless Firebase Web & Admin SDK ingestion.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AppConfig:
    """Production application configuration with environment variable overrides."""

    env: str = os.getenv("ZEN_ENV", "production")
    debug: bool = os.getenv("ZEN_DEBUG", "false").lower() in ("true", "1", "yes")

    # Storage paths & engine selection
    base_dir: Path = Path(__file__).parent
    data_dir: Path = Path(os.getenv("ZEN_DATA_DIR", str(Path(__file__).parent / "data")))
    db_path: Path = Path(os.getenv("ZEN_DB_PATH", str(Path(__file__).parent / "data" / "zen_focus.db")))
    # Options: "auto" (use firestore if credentials present, else sqlite), "sqlite", "firestore"
    storage_backend: str = os.getenv("ZEN_STORAGE_BACKEND", "auto").lower()

    # Security & Execution Limits
    max_tasks_per_query: int = int(os.getenv("ZEN_MAX_TASKS", "500"))
    max_sessions_history: int = int(os.getenv("ZEN_MAX_SESSIONS", "1000"))
    session_timeout_seconds: int = int(os.getenv("ZEN_SESSION_TIMEOUT", "86400"))

    # Production Data Retention & Archival
    default_retention_days: int = int(os.getenv("ZEN_RETENTION_DAYS", "90"))
    enable_auto_retention_prune: bool = os.getenv("ZEN_AUTO_RETENTION", "true").lower() in ("true", "1")

    # Logging
    log_level: str = os.getenv("ZEN_LOG_LEVEL", "INFO")

    def ensure_directories(self) -> None:
        """Ensure necessary runtime directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_firebase_config(self) -> Dict[str, Any]:
        """Load Firebase Client SDK parameters for Google Authentication."""
        # 1. Streamlit Secrets (Production Cloud / .streamlit/secrets.toml)
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "firebase" in st.secrets:
                return dict(st.secrets["firebase"])
        except Exception:
            pass

        # 2. Local config file candidates
        candidates = [
            self.base_dir / "firebase-config.json",
            self.data_dir / "firebase-config.json",
        ]
        for p in candidates:
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    if data.get("projectId") and data.get("apiKey"):
                        return data
                except Exception:
                    pass

        # 3. Environment Variables
        env_project_id = os.getenv("FIREBASE_PROJECT_ID", "")
        if env_project_id:
            return {
                "projectId": env_project_id,
                "apiKey": os.getenv("FIREBASE_API_KEY", ""),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", f"{env_project_id}.firebaseapp.com"),
                "appId": os.getenv("FIREBASE_APP_ID", ""),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", f"{env_project_id}.appspot.com"),
                "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
                "oAuthClientId": os.getenv("FIREBASE_OAUTH_CLIENT_ID", ""),
            }

        # 4. Return unconfigured template (no hardcoded third-party or AI Studio projects)
        return {
            "projectId": "",
            "apiKey": "",
            "authDomain": "",
            "appId": "",
            "storageBucket": "",
            "messagingSenderId": "",
            "oAuthClientId": "",
        }

    @property
    def is_firebase_configured(self) -> bool:
        """Return True if Firebase client credentials have been supplied."""
        cfg = self.get_firebase_config()
        return bool(cfg.get("projectId") and cfg.get("apiKey"))

    def get_firebase_service_account(self) -> Optional[Dict[str, Any]]:
        """Load Firebase Admin Service Account credentials for Cloud Firestore."""
        # 1. Streamlit Secrets
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "firebase_service_account" in st.secrets:
                return dict(st.secrets["firebase_service_account"])
        except Exception:
            pass

        # 2. File candidates
        candidates = [
            self.base_dir / "firebase-service-account.json",
            self.data_dir / "firebase-service-account.json",
        ]
        for p in candidates:
            if p.exists():
                try:
                    return json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass

        # 3. Raw JSON environment variable
        raw_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
        if raw_env:
            try:
                if Path(raw_env).exists():
                    return json.loads(Path(raw_env).read_text(encoding="utf-8"))
                return json.loads(raw_env)
            except Exception:
                pass

        return None


CONFIG = AppConfig()
CONFIG.ensure_directories()
