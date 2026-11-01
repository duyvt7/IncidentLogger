"""
Database package for IT Incident Logger.
Provides connection management and schema migration.
"""
from database.connection import get_connection, create_connection, db_session
from database.schema import init_db

__all__ = ["get_connection", "create_connection", "db_session", "init_db"]
