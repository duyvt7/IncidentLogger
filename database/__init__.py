"""
Database package for IT Incident Logger.
Provides connection management, schema migration, and lazy backward-compatible exports.
"""
from database.connection import get_connection, create_connection, db_session
from database.schema import init_db
from config.settings import get_db_path

DB_PATH = get_db_path()

def __getattr__(name: str):
    """Lazy-loads legacy functions on demand to avoid circular dependencies."""
    if name in (
        "get_incidents",
        "add_incident",
        "update_incident",
        "delete_incident",
        "get_incident_by_id",
        "get_stats",
    ):
        import services.incident_service as inc
        target = "get_incident_statistics" if name == "get_stats" else name
        return getattr(inc, target)

    if name in ("save_hmi_status", "load_hmi_status"):
        import services.hmi_service as hmi
        return getattr(hmi, name)

    if name in (
        "verify_user",
        "list_users",
        "create_user",
        "update_user_password",
        "delete_user",
    ):
        from services.session_service import session_service
        mapping = {
            "verify_user": lambda u, p: session_service.authenticate(u, p)[0],
            "list_users": session_service.get_available_operators,
            "create_user": session_service.create_user,
            "update_user_password": session_service.update_password,
            "delete_user": session_service.delete_user,
        }
        return mapping[name]

    if name == "export_to_excel":
        from services.export_service import export_shift_report_to_excel
        return export_shift_report_to_excel

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "get_connection",
    "create_connection",
    "db_session",
    "init_db",
    "DB_PATH",
]
