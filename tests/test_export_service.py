"""
Unit tests for ExportService (Excel report generation).
"""
import unittest
import tempfile
from pathlib import Path
from datetime import datetime
import openpyxl

from services.export_service import (
    export_shift_report_to_excel,
    get_sheet_tab_name,
)


class TestExportService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "test_shift_report.xlsx"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_shift_report_creates_valid_excel(self):
        dt = datetime(2026, 10, 29, 10, 15)
        incidents = [
            {
                "time": "2026-10-29 10:15",
                "category": "H/W Inspection",
                "sub_category": "MES Server",
                "failure": "Overheating warning",
                "reason": "Fan obstructed",
                "solution": "Cleaned dust from vents",
                "current_situation": "Running normal",
                "contact": "0987654321",
            }
        ]
        hmi_data = {
            "PCM": {"MES link SCC": "OK", "SCC Link PLC": "OK", "Application Link": "OK", "Remark": "Normal"},
            "CAL": {"MES link SCC": "OK", "SCC Link PLC": "OK", "Application Link": "OK", "Remark": ""},
        }

        ok, msg = export_shift_report_to_excel(
            filepath=self.output_path,
            dept="IT",
            section="Dx Engineering Team",
            prepared_by="Vũ Thành Duy",
            shift="Ca Ngày",
            date_val=dt,
            incidents=incidents,
            hmi_data=hmi_data,
        )
        self.assertTrue(ok)
        self.assertTrue(self.output_path.exists())

        # Load back with openpyxl to verify contents
        wb = openpyxl.load_workbook(self.output_path)
        expected_tab = "29-Oct-2026 (Shift 1)"
        self.assertIn(expected_tab, wb.sheetnames)
        ws = wb[expected_tab]

        # Check header
        self.assertEqual(ws["B2"].value, "Dept.: IT")
        self.assertEqual(ws["B3"].value, "Sect.: Dx Engineering Team")
        self.assertEqual(ws["B4"].value, "Prepared by: Vũ Thành Duy")

        # Check incidents in row 23 (MES Server)
        self.assertIn("Overheating warning", str(ws["E23"].value))
        self.assertIn("Cleaned dust from vents", str(ws["G23"].value))

        # Check HMI lines (Row 43: PCM)
        self.assertEqual(ws["B43"].value, "PCM")
        self.assertEqual(ws["C43"].value, "OK")

    def test_export_appends_and_overwrites_tabs(self):
        dt = datetime(2026, 10, 29)
        # 1. Export Shift 1
        ok1, _ = export_shift_report_to_excel(
            filepath=self.output_path,
            shift="Ca Ngày",
            date_val=dt,
        )
        self.assertTrue(ok1)

        # 2. Export Shift 2 to same workbook
        ok2, _ = export_shift_report_to_excel(
            filepath=self.output_path,
            shift="Ca Đêm",
            date_val=dt,
        )
        self.assertTrue(ok2)

        wb = openpyxl.load_workbook(self.output_path)
        self.assertIn("29-Oct-2026 (Shift 1)", wb.sheetnames)
        self.assertIn("29-Oct-2026 (Shift 2)", wb.sheetnames)
        self.assertEqual(len(wb.sheetnames), 2)

        # 3. Re-export Shift 1 to verify safe overwrite
        ok3, _ = export_shift_report_to_excel(
            filepath=self.output_path,
            prepared_by="Updated User",
            shift="Ca Ngày",
            date_val=dt,
        )
        self.assertTrue(ok3)

        wb2 = openpyxl.load_workbook(self.output_path)
        self.assertEqual(wb2["29-Oct-2026 (Shift 1)"]["B4"].value, "Prepared by: Updated User")
        self.assertEqual(len(wb2.sheetnames), 2)


if __name__ == "__main__":
    unittest.main()

