"""
Database Schema Definition and Initialization.

Defines all tables, constraints, indexes, and initial data seeding.
Ensures backward compatibility with existing databases without data loss.
"""
from pathlib import Path
from typing import Optional, Union
import logging

from database.connection import db_session

logger = logging.getLogger(__name__)


def init_db(db_path: Optional[Union[str, Path]] = None) -> None:
    """
    Initializes database schema and ensures all required tables and indexes exist.
    Will never delete or overwrite existing data.
    
    Args:
        db_path: Optional path to the database file. If None, uses default path.
    """
    logger.info("Initializing database schema at: %s", db_path or "default path")

    with db_session(db_path) as conn:
        cursor = conn.cursor()

        # 1. Bảng Sự cố (Incidents)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                time              TEXT    NOT NULL,
                category          TEXT    NOT NULL,
                sub_category      TEXT,
                failure           TEXT    NOT NULL,
                reason            TEXT,
                solution          TEXT,
                current_situation TEXT,
                contact           TEXT,
                reporter          TEXT,
                shift             TEXT,
                created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
        """)

        # Chỉ mục tăng tốc tìm kiếm và lọc thời gian
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_time ON incidents(time);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_category ON incidents(category);
        """)

        # 2. Bảng HMI Monitoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hmi_monitoring (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                line         TEXT    NOT NULL,
                mes_link_scc TEXT,
                scc_link_plc TEXT,
                app_link     TEXT,
                remark       TEXT,
                check_date   TEXT    NOT NULL DEFAULT (date('now'))
            );
        """)

        # 3. Bảng Daily Inspection
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_inspection (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name  TEXT    NOT NULL,
                time_slot  TEXT    NOT NULL,
                status     TEXT    NOT NULL,
                check_date TEXT    NOT NULL DEFAULT (date('now'))
            );
        """)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_insp_unique 
            ON daily_inspection(check_date, item_name, time_slot);
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_inspection_meta (
                check_date       TEXT PRIMARY KEY,
                inspector_shift1 TEXT,
                inspector_shift2 TEXT,
                remark_shift1    TEXT,
                remark_shift2    TEXT,
                details_shift1   TEXT,
                details_shift2   TEXT,
                updated_at       TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
        """)

        # 4. Bảng Users (hỗ trợ sẵn sàng cho phân hệ đăng nhập khi cần)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            );
        """)

        # Seed default users only if the table is completely empty
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            default_users = [
                ("admin", "admin123"),
                ("Hoàng Ngọc Huy", "123"),
                ("Nguyễn Mai Nghĩa", "123"),
                ("Vũ Thành Duy", "123"),
                ("Võ Đình Thủy", "123"),
            ]
            cursor.executemany(
                "INSERT INTO users (username, password) VALUES (?, ?);",
                default_users,
            )
            logger.info("Default seed users created.")

    logger.info("Database schema initialization completed.")
