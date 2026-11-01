"""
Database Connection Manager.

Provides flexible connection management:
1. `get_connection()`: Returns a configured sqlite3.Connection (backward compatible).
2. `db_session()`: Context manager that automatically handles commit, rollback, and close.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union
import sqlite3
import logging

from config.settings import get_db_path

logger = logging.getLogger(__name__)


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """
    Creates and returns a new SQLite database connection with Row factory enabled.
    
    Args:
        db_path: Path to database. If None, resolves default path.
        
    Returns:
        sqlite3.Connection object.
    """
    path = str(db_path or get_db_path())
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


create_connection = get_connection


@contextmanager
def db_session(
    db_path: Optional[Union[str, Path]] = None,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database transactions.
    Automatically commits on success, rolls back on error, and closes the connection.
    
    Usage:
        with db_session() as conn:
            conn.execute("INSERT INTO incidents ...")
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Transaction rolled back due to error: %s", exc)
        raise
    finally:
        conn.close()
