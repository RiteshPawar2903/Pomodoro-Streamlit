"""Firebase Authentication helpers for verifying browser-issued ID tokens."""

from __future__ import annotations

from typing import Any, Dict

import firebase_admin
from firebase_admin import auth, credentials

from config import CONFIG
from models import UserProfile


def _get_firebase_app() -> firebase_admin.App:
    """Return the shared Firebase Admin app, creating it when necessary."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        service_account = CONFIG.get_firebase_service_account()
        if service_account:
            return firebase_admin.initialize_app(credentials.Certificate(service_account))
        return firebase_admin.initialize_app()


def verify_id_token(id_token: str) -> UserProfile:
    """Verify a Firebase ID token and return the authenticated user profile."""
    if not id_token:
        raise ValueError("Firebase ID token is empty.")

    decoded: Dict[str, Any] = auth.verify_id_token(id_token, app=_get_firebase_app())
    uid = decoded.get("uid")
    if not uid:
        raise ValueError("Firebase ID token did not contain a user ID.")

    return UserProfile(
        uid=uid,
        email=decoded.get("email", ""),
        displayName=decoded.get("name", "Zen User"),
        photoURL=decoded.get("picture"),
    )
