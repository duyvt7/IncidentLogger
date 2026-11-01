"""
Incident Management Service.

Encapsulates CRUD operations, filtering, and statistical queries for IT incidents.
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import sqlite3
import logging

from database.connection import db_session

logger = logging.getLogger(__name__)


def add_incident(
    data: Dict[str, Any], db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Inserts a new incident record into the database.
    
    Args:
        data: Dictionary containing incident fields (time, category, failure, etc.)
        db_path: Optional database path override.
        
    Returns:
        The auto-generated ID of the newly inserted incident.
    """
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO incidents 
            (time, category, sub_category, failure, reason, solution, current_situation, contact, reporter, shift)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["time"],
                data["category"],
                data.get("sub_category"),
                data["failure"],
                data.get("reason"),
                data.get("solution"),
                data.get("current_situation"),
                data.get("contact"),
                data.get("reporter"),
                data.get("shift"),
            ),
        )
        incident_id = cursor.lastrowid
        logger.info("Created incident with ID: %s", incident_id)
        return incident_id


def get_incidents(
    search: str = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    reporter: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> List[sqlite3.Row]:
    """
    Queries incidents with flexible filtering by text search, date range, and reporter.
    
    Args:
        search: Substring to search in failure, reason, or contact.
        start_date: Format 'YYYY-MM-DD'.
        end_date: Format 'YYYY-MM-DD'.
        reporter: Optional filter by reporter username/name.
        db_path: Optional database path override.
        
    Returns:
        List of sqlite3.Row matching the criteria, ordered by time DESC.
    """
    query = "SELECT * FROM incidents WHERE 1=1"
    params: List[Any] = []

    if reporter and reporter != "admin":
        query += " AND reporter = ?"
        params.append(reporter)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query += " AND (failure LIKE ? OR reason LIKE ? OR contact LIKE ?)"
        params.extend([term, term, term])

    if start_date and end_date:
        query += " AND SUBSTR(time, 1, 10) BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND SUBSTR(time, 1, 10) >= ?"
        params.append(start_date)
    elif end_date:
        query += " AND SUBSTR(time, 1, 10) <= ?"
        params.append(end_date)

    query += " ORDER BY time DESC"

    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def get_incident_by_id(
    incident_id: int, db_path: Optional[Union[str, Path]] = None
) -> Optional[sqlite3.Row]:
    """Retrieves a single incident by its primary key ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        return cursor.fetchone()


def update_incident(
    incident_id: int,
    data: Dict[str, Any],
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Updates an existing incident record.
    
    Args:
        incident_id: Target record ID.
        data: Updated fields.
        db_path: Optional database path override.
        
    Returns:
        True if record was updated.
    """
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE incidents SET
                time = ?, category = ?, sub_category = ?, failure = ?,
                reason = ?, solution = ?, current_situation = ?, contact = ?
            WHERE id = ?
            """,
            (
                data["time"],
                data["category"],
                data.get("sub_category"),
                data["failure"],
                data.get("reason"),
                data.get("solution"),
                data.get("current_situation"),
                data.get("contact"),
                incident_id,
            ),
        )
        updated = cursor.rowcount > 0
        logger.info("Updated incident ID %s: %s", incident_id, updated)
        return updated


def delete_incident(
    incident_id: int, db_path: Optional[Union[str, Path]] = None
) -> bool:
    """Deletes an incident by ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
        deleted = cursor.rowcount > 0
        logger.info("Deleted incident ID %s: %s", incident_id, deleted)
        return deleted


def get_incident_statistics(
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Gathers key operational metrics for the Dashboard:
    - total: Total number of logged incidents
    - today: Incidents logged today
    - open_issues: Incidents not marked as 'Running normal'
    - by_category: Breakdown of incidents by category
    """
    with db_session(db_path) as conn:
        cursor = conn.cursor()

        # Total
        cursor.execute("SELECT COUNT(*) FROM incidents")
        total = cursor.fetchone()[0]

        # Today
        cursor.execute(
            "SELECT COUNT(*) FROM incidents WHERE SUBSTR(time, 1, 10) = date('now', 'localtime')"
        )
        today_count = cursor.fetchone()[0]

        # Open / In progress
        cursor.execute(
            """
            SELECT COUNT(*) FROM incidents 
            WHERE current_situation != 'Running normal' AND current_situation IS NOT NULL AND current_situation != ''
            """
        )
        open_count = cursor.fetchone()[0]

        # By category
        cursor.execute("SELECT category, COUNT(*) as cnt FROM incidents GROUP BY category")
        by_category = {row["category"]: row["cnt"] for row in cursor.fetchall()}

        return {
            "total": total,
            "today": today_count,
            "open_issues": open_count,
            "by_category": by_category,
        }
