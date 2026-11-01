"""
Database package for IT Incident Logger.
Provides connection management, schema migration, and backward-compatible CRUD operations.
"""
from database.connection import get_connection, create_connection, db_session
from database.schema import init_db
from config.settings import get_db_path

# Backward compatibility exports
from services.incident_service import (
    add_incident,
    get_incidents,
    get_incident_by_id,
    update_incident,
    delete_incident,
    get_incident_statistics as get_stats,
)
from services.hmi_service import save_hmi_status, load_hmi_status
from services.session_service import session_service
from services.export_service import export_shift_report_to_excel as export_to_excel

DB_PATH = get_db_path()

def verify_user(username: str, password: str) -> bool:
    ok, _ = session_service.authenticate(username, password)
    return ok

def list_users() -> list:
    return session_service.get_available_operators()

def create_user(username: str, password: str):
    return session_service.create_user(username, password)

def update_user_password(username: str, new_password: str):
    return session_service.update_password(username, new_password)

def delete_user(username: str):
    return session_service.delete_user(username)

__all__ = [
    "get_connection",
    "create_connection",
    "db_session",
    "init_db",
    "DB_PATH",
    "get_db_path",
    "verify_user",
    "list_users",
    "create_user",
    "update_user_password",
    "delete_user",
    "add_incident",
    "get_incidents",
    "get_incident_by_id",
    "update_incident",
    "delete_incident",
    "get_stats",
    "save_hmi_status",
    "load_hmi_status",
    "export_to_excel",
]
