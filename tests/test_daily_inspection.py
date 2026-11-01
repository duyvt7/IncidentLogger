"""
Unit tests for Daily Inspection Service and Exporter.
"""
import unittest
import tempfile
from pathlib import Path
from datetime import datetime
import openpyxl

from database.schema import init_db
from services.daily_inspection_service import (
    ALL_HOURS,
    SHIFT_1_HOURS,
    SHIFT_2_HOURS,
    INSPECTION_ITEMS,
    generate_default_daily_data,
    save_daily_inspection,
    load_daily_inspection,
    export_daily_inspection_to_excel,
    get_daily_sheet_name,
)


class TestDailyInspectionService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_daily.db"
        init_db(self.db_path)
        self.excel_path = Path(self.temp_dir.name) / "Daily inspection 10-2026.xlsx"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generate_default_daily_data(self):
        date_str = "2026-10-29"
        data = generate_default_daily_data(date_str, inspector_shift1="Nghia", inspector_shift2="Huy")

        self.assertEqual(data["date"], date_str)
        self.assertEqual(len(data["items"]), len(INSPECTION_ITEMS))
        self.assertEqual(data["items"]["Temp (°C)"]["8:00"], "22°C")
        self.assertEqual(data["items"]["Humidity(%)"]["14:00"], "46%")
        self.assertEqual(data["items"]["MES server"]["8:00"], "V")
        self.assertEqual(data["items"]["Man IN-OUT"]["20:00"], "-")
        self.assertEqual(data["inspectors"]["8:00"], "Nghia")
        self.assertEqual(data["inspectors"]["20:00"], "Huy")

    def test_save_and_load_daily_inspection(self):
        date_str = "2026-10-29"
        data = generate_default_daily_data(date_str, inspector_shift1="Nghia", inspector_shift2="Huy")
        # Simulate toggling a failure
        data["items"]["MES server"]["10:00"] = "X"
        data["remarks"]["shift1"] = "Server rebooted"

        ok, msg = save_daily_inspection(date_str, data, db_path=self.db_path)
        self.assertTrue(ok)

        loaded = load_daily_inspection(date_str, db_path=self.db_path)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["items"]["MES server"]["10:00"], "X")
        self.assertEqual(loaded["items"]["MES server"]["8:00"], "V")
        self.assertEqual(loaded["remarks"]["shift1"], "Server rebooted")
        self.assertEqual(loaded["inspectors"]["8:00"], "Nghia")
        self.assertEqual(loaded["inspectors"]["20:00"], "Huy")

    def test_export_daily_inspection_creates_correct_tab_format(self):
        date_str = "2026-10-29"
        data = generate_default_daily_data(date_str, inspector_shift1="Nghia", inspector_shift2="Huy")
        data["items"]["MES server"]["10:00"] = "X"

        ok, msg = export_daily_inspection_to_excel(
            date_str=date_str,
            data=data,
            filepath=self.excel_path,
        )
        self.assertTrue(ok)
        self.assertTrue(self.excel_path.exists())

        wb = openpyxl.load_workbook(self.excel_path)
        expected_tab = "29-10-2026"
        self.assertIn(expected_tab, wb.sheetnames)
        ws = wb[expected_tab]

        # Shift headers in row 1
        self.assertEqual(ws["C1"].value, "1st Shift")
        self.assertEqual(ws["O1"].value, "2nd Shift")

        # Hourly headers in row 2
        self.assertEqual(ws["C2"].value, "8:00")
        self.assertEqual(ws["O2"].value, "20:00")
        self.assertEqual(ws["Z2"].value, "7:00")

        # Temp & Humidity (Rows 3 & 4)
        self.assertEqual(ws["A3"].value, "Temp (°C)")
        self.assertEqual(ws["C3"].value, "22°C")
        self.assertEqual(ws["A4"].value, "Humidity(%)")
        self.assertEqual(ws["C4"].value, "46%")

        # MES server (Row 5): normal at 8:00 (col C), abnormal at 10:00 (col E)
        self.assertEqual(ws["A5"].value, "Server")
        self.assertEqual(ws["B5"].value, "MES server")
        self.assertEqual(ws["C5"].value, "V")
        self.assertEqual(ws["E5"].value, "X")

        # Man IN-OUT (Row 29)
        self.assertEqual(ws["A29"].value, "Man IN-OUT")
        self.assertEqual(ws["C29"].value, "-")

        # Legend at bottom
        self.assertEqual(ws["A34"].value, "V : Normal")
        self.assertEqual(ws["A35"].value, "X : Abnormal")

    def test_export_multiple_dates_appends_tabs(self):
        for day in (28, 29, 30):
            date_str = f"2026-10-{day}"
            data = generate_default_daily_data(date_str)
            ok, _ = export_daily_inspection_to_excel(
                date_str=date_str,
                data=data,
                filepath=self.excel_path,
            )
            self.assertTrue(ok)

        wb = openpyxl.load_workbook(self.excel_path)
        self.assertIn("28-10-2026", wb.sheetnames)
        self.assertIn("29-10-2026", wb.sheetnames)
        self.assertIn("30-10-2026", wb.sheetnames)
        self.assertEqual(len(wb.sheetnames), 3)


if __name__ == "__main__":
    unittest.main()
