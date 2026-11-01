"""
Session and Authentication Service.

Manages the active shift operator and provides an extensible authentication
interface ready for future login system activation without disrupting application flow.
"""
from typing import List, Optional, Tuple
from pathlib import Path
import hashlib
import secrets
import logging

from config.settings import AppSettings
from config.constants import DEFAULT_OPERATORS
from database.connection import db_session, get_connection

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a cryptographically secure random salt.
    Format: pbkdf2:sha256:100000$<salt_hex>$<hash_hex>
    """
    salt = secrets.token_hex(16)
    iterations = 100000
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2:sha256:{iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verifies a password against the stored password.
    Supports both modern PBKDF2 hashes and legacy plain-text passwords for seamless backward compatibility.
    """
    if stored_password.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_password.split(":")
            # parts: ['pbkdf2', 'sha256', '<iterations>$<salt>$<hash>']
            payload = parts[2]
            iter_str, salt, stored_hash = payload.split("$")
            iterations = int(iter_str)
            key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations)
            return secrets.compare_digest(key.hex(), stored_hash)
        except Exception as exc:
            logger.error("Error parsing password hash: %s", exc)
            return False
    # Legacy plaintext password fallback
    return secrets.compare_digest(plain_password, stored_password)


class SessionService:
    """
    Session manager tracking the currently active operator.
    Designed with extension points for full authentication and user management.
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or AppSettings()
        # Default operator is the first in DEFAULT_OPERATORS
        self._current_operator: str = DEFAULT_OPERATORS[0]

    @property
    def current_operator(self) -> str:
        """Returns the name of the active operator."""
        return self._current_operator

    @current_operator.setter
    def current_operator(self, name: str) -> None:
        """Sets the active operator."""
        if name and name.strip():
            self._current_operator = name.strip()
            logger.info("Current operator switched to: %s", self._current_operator)

    def is_auth_enabled(self) -> bool:
        """Checks if login screen is required."""
        return self.settings.auth_enabled

    def get_available_operators(self, db_path: Optional[Path] = None) -> List[str]:
        """
        Retrieves the list of available operators from the database 'users' table,
        falling back to DEFAULT_OPERATORS if database is empty or unavailable.
        """
        try:
            with db_session(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users ORDER BY username ASC")
                rows = cursor.fetchall()
                if rows:
                    users = [r["username"] for r in rows if r["username"] != "admin"]
                    # Add admin at the end of the list
                    users.append("admin")
                    return users
        except Exception as exc:
            logger.warning("Could not fetch users from database, using defaults: %s", exc)
        return DEFAULT_OPERATORS

    # ══════════════════════════════════════════════════════════════
    # Extensible Auth Backend Methods (For future login development)
    # ══════════════════════════════════════════════════════════════
    def authenticate(
        self, username: str, password: str, db_path: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """
        Validates username and password.
        Automatically upgrades legacy plaintext passwords to secure PBKDF2 hashes on success.
        """
        try:
            with db_session(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT username, password FROM users WHERE username = ?",
                    (username,),
                )
                row = cursor.fetchone()
                if not row:
                    return False, "Tài khoản không tồn tại."

                stored_pwd = row["password"]
                if verify_password(password, stored_pwd):
                    self.current_operator = username

                    # Upgrade plaintext password to hash if needed
                    if not stored_pwd.startswith("pbkdf2:sha256:"):
                        new_hash = hash_password(password)
                        cursor.execute(
                            "UPDATE users SET password = ? WHERE username = ?",
                            (new_hash, username),
                        )
                        logger.info("Migrated user '%s' password to PBKDF2 hash.", username)

                    return True, "Đăng nhập thành công!"
                return False, "Mật khẩu không chính xác."
        except Exception as exc:
            logger.error("Authentication error: %s", exc)
            return False, f"Lỗi hệ thống: {exc}"

    def create_user(
        self, username: str, password: str, db_path: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """Creates a new user with a hashed password."""
        uname = username.strip()
        pwd = password.strip()
        if not uname or not pwd:
            return False, "Username và mật khẩu không được để trống."

        hashed = hash_password(pwd)
        try:
            with db_session(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (uname, hashed),
                )
                return True, f"Tạo tài khoản '{uname}' thành công!"
        except Exception as exc:
            logger.error("Failed to create user '%s': %s", uname, exc)
            return False, f"Lỗi tạo user: {exc}"

    def update_password(
        self, username: str, new_password: str, db_path: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """Updates a user's password with a secure hash."""
        pwd = new_password.strip()
        if not pwd:
            return False, "Mật khẩu mới không được để trống."

        hashed = hash_password(pwd)
        try:
            with db_session(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hashed, username),
                )
                return True, f"Đã cập nhật mật khẩu cho '{username}'."
        except Exception as exc:
            return False, f"Lỗi cập nhật mật khẩu: {exc}"

    def delete_user(
        self, username: str, db_path: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """Deletes a user (admin cannot be deleted)."""
        if username.lower() == "admin":
            return False, "Không thể xóa tài khoản admin mặc định."
        try:
            with db_session(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                return True, f"Đã xóa tài khoản '{username}'."
        except Exception as exc:
            return False, f"Lỗi xóa user: {exc}"


# Singleton session service instance
session_service = SessionService()
