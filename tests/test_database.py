"""
Unit tests for database connection and schema initialization.
Uses temporary SQLite database files to avoid modifying production data.
"""
import unittest
import tempfile
from pathlib import Path
import sqlite3

from database.connection import get_connection, db_session
from database.schema import init_db


class TestDatabaseConnectionAndSchema(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_db_creates_all_tables(self):
        init_db(self.db_path)
        self.assertTrue(self.db_path.exists())

        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        conn.close()

        expected = ["incidents", "hmi_monitoring", "daily_inspection", "users"]
        for table in expected:
            self.assertIn(table, tables, f"Table '{table}' should have been created.")

    def test_init_db_seeds_default_users_only_once(self):
        init_db(self.db_path)

        with db_session(self.db_path) as conn:
            count1 = conn.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
            self.assertEqual(count1, 5)

        # Run init_db a second time; user count should stay at 5
        init_db(self.db_path)
        with db_session(self.db_path) as conn:
            count2 = conn.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
            self.assertEqual(count2, 5)

    def test_transaction_rollback_on_exception(self):
        init_db(self.db_path)

        with self.assertRaises(ValueError):
            with db_session(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO incidents (time, category, failure) VALUES (?, ?, ?)",
                    ("2026-11-01 10:00", "H/W Inspection", "Failure A"),
                )
                raise ValueError("Simulated error to trigger rollback")

        with db_session(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM incidents;").fetchone()[0]
            self.assertEqual(count, 0, "Record should have been rolled back.")


if __name__ == "__main__":
    unittest.main()
