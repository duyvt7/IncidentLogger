"""
Unit tests for SessionService and authentication extensions.
"""
import unittest
import tempfile
from pathlib import Path

from database.schema import init_db
from database.connection import db_session
from services.session_service import (
    SessionService,
    hash_password,
    verify_password,
)


class TestSessionService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_session.db"
        init_db(self.db_path)
        self.service = SessionService()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_current_operator_property(self):
        self.assertIsNotNone(self.service.current_operator)
        self.service.current_operator = "Nguyễn Mai Nghĩa"
        self.assertEqual(self.service.current_operator, "Nguyễn Mai Nghĩa")

    def test_get_available_operators(self):
        operators = self.service.get_available_operators(self.db_path)
        self.assertIn("admin", operators)
        self.assertIn("Vũ Thành Duy", operators)

    def test_password_hash_and_verification(self):
        plain = "MySecretPass@123"
        hashed = hash_password(plain)
        self.assertTrue(hashed.startswith("pbkdf2:sha256:"))
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("WrongPass", hashed))

    def test_authenticate_with_plaintext_and_auto_upgrade(self):
        # Default seed user 'admin' has plaintext 'admin123'
        ok, msg = self.service.authenticate("admin", "admin123", self.db_path)
        self.assertTrue(ok)
        self.assertEqual(self.service.current_operator, "admin")

        # Verify password in DB was auto-upgraded to PBKDF2 hash
        with db_session(self.db_path) as conn:
            row = conn.execute("SELECT password FROM users WHERE username='admin'").fetchone()
            self.assertTrue(row["password"].startswith("pbkdf2:sha256:"))

    def test_user_crud(self):
        # Create user
        ok, _ = self.service.create_user("testuser", "pass123", self.db_path)
        self.assertTrue(ok)

        # Authenticate with new user
        auth_ok, _ = self.service.authenticate("testuser", "pass123", self.db_path)
        self.assertTrue(auth_ok)

        # Update password
        upd_ok, _ = self.service.update_password("testuser", "newpass456", self.db_path)
        self.assertTrue(upd_ok)
        auth_new_ok, _ = self.service.authenticate("testuser", "newpass456", self.db_path)
        self.assertTrue(auth_new_ok)

        # Cannot delete admin
        del_admin_ok, _ = self.service.delete_user("admin", self.db_path)
        self.assertFalse(del_admin_ok)

        # Can delete testuser
        del_ok, _ = self.service.delete_user("testuser", self.db_path)
        self.assertTrue(del_ok)


if __name__ == "__main__":
    unittest.main()

