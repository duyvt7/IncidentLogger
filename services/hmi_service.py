"""
HMI Monitoring Service.

Manages persisting and retrieving HMI line connection health checks.
"""
from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging

from database.connection import db_session

logger = logging.getLogger(__name__)


def save_hmi_status(
    hmi_dict: Dict[str, Dict[str, str]],
    db_path: Optional[Union[str, Path]] = None,
) -> None:
    """
    Saves the HMI line statuses into the database.
    Replaces existing records with the latest status.
    
    Args:
        hmi_dict: Dictionary mapping line names to column values.
        db_path: Optional database path override.
    """
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hmi_monitoring")
        for line, cols in hmi_dict.items():
            cursor.execute(
                """
                INSERT INTO hmi_monitoring (line, mes_link_scc, scc_link_plc, app_link, remark)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    line,
                    cols.get("MES link SCC"),
                    cols.get("SCC Link PLC"),
                    cols.get("Application Link"),
                    cols.get("Remark"),
                ),
            )
        logger.info("Saved HMI status for %d lines.", len(hmi_dict))


def load_hmi_status(
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Loads all saved HMI line connection statuses from the database.
    
    Returns:
        Dictionary mapping line names to their column values.
    """
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hmi_monitoring")
        rows = cursor.fetchall()
        result: Dict[str, Dict[str, str]] = {}
        for r in rows:
            result[r["line"]] = {
                "MES link SCC": r["mes_link_scc"] or "OK",
                "SCC Link PLC": r["scc_link_plc"] or "OK",
                "Application Link": r["app_link"] or "OK",
                "Remark": r["remark"] or "",
            }
        return result
