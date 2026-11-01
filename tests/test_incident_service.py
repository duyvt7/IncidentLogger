"""
Unit tests for IncidentService and HMIService.
"""
import unittest
import tempfile
from pathlib import Path

from database.schema import init_db
from services.incident_service import (
    add_incident,
    get_incidents,
    get_incident_by_id,
    update_incident,
    delete_incident,
    get_incident_statistics,
)
from services.hmi_service import save_hmi_status, load_hmi_status


class TestIncidentAndHmiServices(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_incidents.db"
        init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_get_incident(self):
        data = {
            "time": "2026-11-01 08:30",
            "category": "H/W Inspection",
            "sub_category": "MES Server",
            "failure": "Server unreachable",
            "reason": "Network cable loose",
            "solution": "Reconnected cable",
            "current_situation": "Running normal",
            "contact": "123456",
            "reporter": "Hoàng Ngọc Huy",
            "shift": "Ca Ngày",
        }
        iid = add_incident(data, self.db_path)
        self.assertGreater(iid, 0)

        # Retrieve by id
        row = get_incident_by_id(iid, self.db_path)
        self.assertIsNotNone(row)
        self.assertEqual(row["failure"], "Server unreachable")
        self.assertEqual(row["reporter"], "Hoàng Ngọc Huy")

    def test_filter_incidents(self):
        add_incident({
            "time": "2026-10-20 10:00",
            "category": "Facility Inspection",
            "failure": "Air conditioning water leak",
            "reporter": "Vũ Thành Duy",
        }, self.db_path)

        add_incident({
            "time": "2026-11-01 14:00",
            "category": "H/W Inspection",
            "failure": "MES Printer paper jam",
            "reporter": "Hoàng Ngọc Huy",
        }, self.db_path)

        # Search term filter
        res_search = get_incidents(search="Printer", db_path=self.db_path)
        self.assertEqual(len(res_search), 1)
        self.assertEqual(res_search[0]["category"], "H/W Inspection")

        # Date range filter
        res_date = get_incidents(
            start_date="2026-11-01", end_date="2026-11-01", db_path=self.db_path
        )
        self.assertEqual(len(res_date), 1)

        # Reporter filter
        res_reporter = get_incidents(reporter="Vũ Thành Duy", db_path=self.db_path)
        self.assertEqual(len(res_reporter), 1)

    def test_update_and_delete_incident(self):
        iid = add_incident({
            "time": "2026-11-01 09:00",
            "category": "Security Inspection",
            "failure": "Window lock loose",
        }, self.db_path)

        # Update
        updated = update_incident(
            iid,
            {
                "time": "2026-11-01 09:00",
                "category": "Security Inspection",
                "sub_category": "Locks (doors & windows)",
                "failure": "Window lock repaired",
                "current_situation": "Running normal",
            },
            self.db_path,
        )
        self.assertTrue(updated)

        row = get_incident_by_id(iid, self.db_path)
        self.assertEqual(row["failure"], "Window lock repaired")

        # Delete
        deleted = delete_incident(iid, self.db_path)
        self.assertTrue(deleted)
        self.assertIsNone(get_incident_by_id(iid, self.db_path))

    def test_incident_statistics(self):
        add_incident({
            "time": "2026-11-01 08:00",
            "category": "Indoor Environment",
            "failure": "Temp 28C",
            "current_situation": "Đang xử lí",
        }, self.db_path)

        stats = get_incident_statistics(self.db_path)
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["open_issues"], 1)
        self.assertEqual(stats["by_category"].get("Indoor Environment"), 1)

    def test_hmi_save_and_load(self):
        data = {
            "PCM": {"MES link SCC": "OK", "SCC Link PLC": "Stopped", "Application Link": "OK", "Remark": "Line maintenance"},
            "CAL": {"MES link SCC": "OK", "SCC Link PLC": "OK", "Application Link": "OK", "Remark": ""},
        }
        save_hmi_status(data, self.db_path)

        loaded = load_hmi_status(self.db_path)
        self.assertIn("PCM", loaded)
        self.assertEqual(loaded["PCM"]["SCC Link PLC"], "Stopped")
        self.assertEqual(loaded["PCM"]["Remark"], "Line maintenance")
        self.assertEqual(loaded["CAL"]["MES link SCC"], "OK")


if __name__ == "__main__":
    unittest.main()
