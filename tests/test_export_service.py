"""
Unit tests for ExportService (Excel report generation).
"""
import unittest
import tempfile
from pathlib import Path
import openpyxl

from services.export_service import export_shift_report_to_excel


class TestExportService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "test_shift_report.xlsx"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_shift_report_creates_valid_excel(self):
        incidents = [
            {
                "time": "2026-11-01 10:15",
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
            dept="IT Operation",
            prepared_by="Vũ Thành Duy",
            shift="Ca Ngày",
            incidents=incidents,
            hmi_data=hmi_data,
        )
        self.assertTrue(ok)
        self.assertTrue(self.output_path.exists())

        # Load back with openpyxl to verify contents
        wb = openpyxl.load_workbook(self.output_path)
        self.assertIn("Shift Report", wb.sheetnames)
        ws = wb["Shift Report"]

        # Check header
        self.assertEqual(ws["B2"].value, "Dept.: IT Operation")
        self.assertEqual(ws["B4"].value, "Prepared by: Vũ Thành Duy")

        # Check incidents in row 24 (MES Server)
        self.assertIn("Overheating warning", str(ws["E24"].value))
        self.assertIn("Cleaned dust from vents", str(ws["G24"].value))

        # Check HMI lines (Row 44: PCM)
        self.assertEqual(ws["B44"].value, "PCM")
        self.assertEqual(ws["C44"].value, "OK")


if __name__ == "__main__":
    unittest.main()

