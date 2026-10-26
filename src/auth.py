"""
Role-Based Access Control (RBAC) & Privacy Guard for MediGuide AI.
Enforces patient privacy (NABH / DISHA compliance) by separating Individual Patient
self-service access from Hospital Staff & Administrator master access.
"""

import streamlit as st
from src.config import get_secret

DEFAULT_ADMIN_PASSKEY = "admin123"


def get_admin_passkey() -> str:
    """Retrieve configured admin passkey from secrets or fallback to default."""
    return get_secret("ADMIN_PASSKEY", DEFAULT_ADMIN_PASSKEY)


def is_admin() -> bool:
    """Check if the current session has authenticated as Hospital Clinician / Admin."""
    return bool(st.session_state.get("is_admin_authenticated", False))


def authenticate_admin(passkey: str) -> bool:
    """Verify administrator passkey and establish elevated session if valid."""
    correct_passkey = get_admin_passkey()
    if passkey and passkey.strip() == correct_passkey:
        st.session_state["is_admin_authenticated"] = True
        return True
    return False


def logout_admin():
    """Revoke administrator privileges and return to individual patient mode."""
    st.session_state["is_admin_authenticated"] = False
