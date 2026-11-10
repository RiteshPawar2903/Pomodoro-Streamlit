"""
Configuration module for Zen Pomodoro Clock.
Follows IEEE Std 828 / 12207 configuration management and environment isolation standards.
Supports zero-hardcoded configuration with seamless Firebase Web & Admin SDK ingestion.
Handles snake_case and camelCase normalization across Streamlit Secrets, JSON files, and Env vars.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


def _normalize_firebase_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize user-provided Firebase configuration across naming conventions."""
    if not isinstance(raw, dict):
        return {}

    project_id = (
        raw.get("projectId")
        or raw.get("project_id")
        or raw.get("FIREBASE_PROJECT_ID")
        or ""
    )
    api_key = (
        raw.get("apiKey")
        or raw.get("api_key")
        or raw.get("FIREBASE_API_KEY")
        or ""
    )
    auth_domain = (
        raw.get("authDomain")
        or raw.get("auth_domain")
        or raw.get("FIREBASE_AUTH_DOMAIN")
        or (f"{project_id}.firebaseapp.com" if project_id else "")
    )
    app_id = (
        raw.get("appId")
        or raw.get("app_id")
        or raw.get("FIREBASE_APP_ID")
        or ""
    )
    storage_bucket = (
        raw.get("storageBucket")
        or raw.get("storage_bucket")
        or raw.get("FIREBASE_STORAGE_BUCKET")
        or (f"{project_id}.appspot.com" if project_id else "")
    )
    messaging_sender_id = (
        raw.get("messagingSenderId")
        or raw.get("messaging_sender_id")
        or raw.get("FIREBASE_MESSAGING_SENDER_ID")
        or ""
    )
    measurement_id = (
        raw.get("measurementId")
        or raw.get("measurement_id")
        or raw.get("FIREBASE_MEASUREMENT_ID")
        or ""
    )
    oauth_client_id = (
        raw.get("oAuthClientId")
        or raw.get("oauth_client_id")
        or raw.get("FIREBASE_OAUTH_CLIENT_ID")
        or ""
    )

    return {
        "projectId": project_id,
        "apiKey": api_key,
        "authDomain": auth_domain,
        "appId": app_id,
        "storageBucket": storage_bucket,
        "messagingSenderId": messaging_sender_id,
        "measurementId": measurement_id,
        "oAuthClientId": oauth_client_id,
    }


def _normalize_service_account(raw: Any) -> Optional[Dict[str, Any]]:
    """Normalize service account credentials, auto-parsing JSON strings and fixing escaped newlines."""
    if not raw:
        return None

    data: Dict[str, Any] = {}
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except Exception:
            return None
    elif isinstance(raw, dict):
        data = dict(raw)
    else:
        return None

    # Handle escaped newlines in private key if entered via single-line text secrets
    if "private_key" in data and isinstance(data["private_key"], str):
        if "\\n" in data["private_key"]:
            data["private_key"] = data["private_key"].replace("\\n", "\n")

    if data.get("client_email") and data.get("private_key"):
        return data
    return None


def verify_firebase_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Verify a Firebase client ID token and return its decoded claims."""
    if not id_token:
        return None

    try:
        import firebase_admin
        from firebase_admin import auth, credentials

        try:
            app = firebase_admin.get_app()
        except ValueError:
            service_account = CONFIG.get_firebase_service_account()
            if service_account:
                app = firebase_admin.initialize_app(credentials.Certificate(service_account))
            else:
                app = firebase_admin.initialize_app()

        return auth.verify_id_token(id_token, app=app)
    except (ValueError, KeyError, TypeError):
        return None
    except Exception:
        return None


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
        """Load Firebase Client SDK parameters for Google Authentication across all sources."""
        # 1. Streamlit Secrets (Production Cloud / .streamlit/secrets.toml)
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                # Nested tables
                for sec_key in ("firebase", "firebase_client", "firebase_config"):
                    if sec_key in st.secrets:
                        norm = _normalize_firebase_config(dict(st.secrets[sec_key]))
                        if norm.get("projectId") and norm.get("apiKey"):
                            return norm

                # Top-level secrets in secrets.toml
                root_dict = dict(st.secrets)
                norm = _normalize_firebase_config(root_dict)
                if norm.get("projectId") and norm.get("apiKey"):
                    return norm
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
                    norm = _normalize_firebase_config(data)
                    if norm.get("projectId") and norm.get("apiKey"):
                        return norm
                except Exception:
                    pass

        # 3. Environment Variables
        env_dict = {
            "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
            "apiKey": os.getenv("FIREBASE_API_KEY", ""),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
            "appId": os.getenv("FIREBASE_APP_ID", ""),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
            "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
            "oAuthClientId": os.getenv("FIREBASE_OAUTH_CLIENT_ID", ""),
        }
        norm = _normalize_firebase_config(env_dict)
        if norm.get("projectId") and norm.get("apiKey"):
            return norm

        # 4. Return unconfigured template
        return {
            "projectId": "",
            "apiKey": "",
            "authDomain": "",
            "appId": "",
            "storageBucket": "",
            "messagingSenderId": "",
            "measurementId": "",
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
            if hasattr(st, "secrets"):
                for sec_key in ("firebase_service_account", "service_account", "gcp_service_account"):
                    if sec_key in st.secrets:
                        parsed = _normalize_service_account(st.secrets[sec_key])
                        if parsed:
                            return parsed
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
                    parsed = _normalize_service_account(p.read_text(encoding="utf-8"))
                    if parsed:
                        return parsed
                except Exception:
                    pass

        # 3. Environment variable (path or inline JSON)
        raw_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
        if raw_env:
            try:
                if Path(raw_env).exists():
                    parsed = _normalize_service_account(Path(raw_env).read_text(encoding="utf-8"))
                else:
                    parsed = _normalize_service_account(raw_env)
                if parsed:
                    return parsed
            except Exception:
                pass

        return None


CONFIG = AppConfig()
CONFIG.ensure_directories()
