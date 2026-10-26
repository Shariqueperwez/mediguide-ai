"""
Unit tests for Role-Based Access Control (RBAC) & Staff Authentication in MediGuide AI.
"""

import unittest
from unittest.mock import patch
from src.auth import authenticate_admin, is_admin, logout_admin, DEFAULT_ADMIN_PASSKEY


class TestAuth(unittest.TestCase):
    def setUp(self):
        # Mock streamlit session_state as a dict
        self.session_dict = {}
        self.patcher = patch("streamlit.session_state", self.session_dict)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_default_patient_mode_is_not_admin(self):
        self.assertFalse(is_admin())

    def test_admin_authentication_success(self):
        self.assertTrue(authenticate_admin(DEFAULT_ADMIN_PASSKEY))
        self.assertTrue(is_admin())

    def test_admin_authentication_failure(self):
        self.assertFalse(authenticate_admin("wrong_password"))
        self.assertFalse(is_admin())

    def test_admin_logout(self):
        authenticate_admin(DEFAULT_ADMIN_PASSKEY)
        self.assertTrue(is_admin())
        logout_admin()
        self.assertFalse(is_admin())


if __name__ == "__main__":
    unittest.main()
