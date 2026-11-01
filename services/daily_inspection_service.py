"""
Daily Inspection Service.

Manages data model, SQLite persistence, default data generation, and Excel export
for the 24-hour IT Daily Inspection sheet matching Image 4.
Master file destination: D:\\Report\\<YYYY>\\<Month>\\Daily inspection <MM-YYYY>.xlsx
Sheet tab name: DD-MM-YYYY (e.g. 29-10-2026)
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import logging

from config.settings import get_app_dir
from database.connection import db_session
from services.export_service import get_default_report_dir

logger = logging.getLogger(__name__)

# ── 1. Hourly Time Slots (24 Hours) ──
SHIFT_1_HOURS = [
    "8:00", "9:00", "10:00", "11:00", "12:00", "13:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"
]
SHIFT_2_HOURS = [
    "20:00", "21:00", "22:00", "23:00", "0:00", "1:00",
    "2:00", "3:00", "4:00", "5:00", "6:00", "7:00"
]
ALL_HOURS = SHIFT_1_HOURS + SHIFT_2_HOURS

# Mapping hours to Excel columns (C to Z)
HOUR_TO_COL = {
    hour: chr(ord('C') + idx) if idx < 24 else "Z"
    for idx, hour in enumerate(ALL_HOURS)
}

# ── 2. Inspection Items Specification Matching Image 4 ──
# (row_index, category_name_in_col_A, item_name_in_col_B, default_val)
INSPECTION_ITEMS = [
    (3, None, "Temp (°C)", "22°C"),
    (4, None, "Humidity(%)", "46%"),
    (5, "Server", "MES server", "V"),
    (6, "Server", "HMI Server", "V"),
    (7, "Server", "CLTS server", "V"),
    (8, "Server", "Virus Chaer, etc..", "V"),
    (9, "Storage", "MES", "V"),
    (10, "Storage", "HMI", "V"),
    (11, None, "Back-up devices", "V"),
    (12, "Network", "Router", "V"),
    (13, "Network", "Firewall", "V"),
    (14, "Network", "Proxy", "V"),
    (15, "Network", "Core", "V"),
    (16, "Network", "Call Manager", "V"),
    (17, "Network", "MES Server SW", "V"),
    (18, "Network", "[FA] Switch", "V"),
    (19, "Network", "[OA] Switch", "V"),
    (20, "Network", "IPMS", "V"),
    (21, "Network", "ISP Devices", "V"),
    (22, "UPS", "Display", "V"),
    (23, "UPS", "Log", "V"),
    (24, "UPS", "Battery", "V"),
    (25, "Air condition", "Air condition", "V"),
    (26, "Air condition", "Control Panel", "V"),
    (27, None, "Fire, Water leaks", "V"),
    (28, None, "Fire extinguisher", "V"),
    (29, None, "Man IN-OUT", "-"),
    (30, None, "Locks (doors & windows)", "V"),
]


def get_daily_inspection_master_path(dt: Optional[datetime] = None) -> Path:
    """
    Returns full path to monthly Daily Inspection master workbook:
    D:\\Report\\<YYYY>\\<Month>\\Daily inspection <MM-YYYY>.xlsx
    """
    date_obj = dt or datetime.now()
    folder = get_default_report_dir(date_obj)
    filename = f"Daily inspection {date_obj.strftime('%m-%Y')}.xlsx"
    return folder / filename


def get_daily_sheet_name(dt: datetime) -> str:
    """Returns standardized tab name matching Image 4: 'DD-MM-YYYY' (e.g. 29-10-2026)."""
    return dt.strftime("%d-%m-%Y")


def generate_default_daily_data(
    date_str: str,
    inspector_shift1: str = "Nghia",
    inspector_shift2: str = "Huy",
) -> Dict[str, Any]:
    """
    Generates standard initial inspection dataset with default values:
    - Temp: 22°C
    - Humidity: 46%
    - Equipment status: 'V'
    - Man IN-OUT: '-'
    - Inspectors assigned to Shift 1 and Shift 2 hours
    """
    items_data: Dict[str, Dict[str, str]] = {}
    for _, _, item_name, def_val in INSPECTION_ITEMS:
        items_data[item_name] = {hour: def_val for hour in ALL_HOURS}

    inspectors_data: Dict[str, str] = {
        hour: (inspector_shift1 if hour in SHIFT_1_HOURS else inspector_shift2)
        for hour in ALL_HOURS
    }

    return {
        "date": date_str,
        "items": items_data,
        "inspectors": inspectors_data,
        "remarks": {"shift1": "", "shift2": ""},
        "details": {"shift1": "", "shift2": ""},
    }


def save_daily_inspection(
    date_str: str,
    data: Dict[str, Any],
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """
    Persists inspection grid and meta into SQLite tables:
    `daily_inspection` and `daily_inspection_meta`.
    """
    try:
        with db_session(db_path) as conn:
            cursor = conn.cursor()

            # 1. Upsert grid items
            items = data.get("items", {})
            for item_name, hour_dict in items.items():
                for hour, val in hour_dict.items():
                    cursor.execute("""
                        INSERT INTO daily_inspection (check_date, item_name, time_slot, status)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(check_date, item_name, time_slot)
                        DO UPDATE SET status = excluded.status;
                    """, (date_str, item_name, hour, str(val)))

            # 2. Upsert inspector hours
            inspectors = data.get("inspectors", {})
            for hour, insp_name in inspectors.items():
                cursor.execute("""
                    INSERT INTO daily_inspection (check_date, item_name, time_slot, status)
                    VALUES (?, 'Inspected by', ?, ?)
                    ON CONFLICT(check_date, item_name, time_slot)
                    DO UPDATE SET status = excluded.status;
                """, (date_str, hour, str(insp_name)))

            # 3. Upsert metadata
            remarks = data.get("remarks", {})
            details = data.get("details", {})
            insp_s1 = inspectors.get("8:00", "")
            insp_s2 = inspectors.get("20:00", "")

            cursor.execute("""
                INSERT INTO daily_inspection_meta (
                    check_date, inspector_shift1, inspector_shift2,
                    remark_shift1, remark_shift2, details_shift1, details_shift2, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                ON CONFLICT(check_date) DO UPDATE SET
                    inspector_shift1 = excluded.inspector_shift1,
                    inspector_shift2 = excluded.inspector_shift2,
                    remark_shift1 = excluded.remark_shift1,
                    remark_shift2 = excluded.remark_shift2,
                    details_shift1 = excluded.details_shift1,
                    details_shift2 = excluded.details_shift2,
                    updated_at = excluded.updated_at;
            """, (
                date_str,
                insp_s1,
                insp_s2,
                remarks.get("shift1", ""),
                remarks.get("shift2", ""),
                details.get("shift1", ""),
                details.get("shift2", ""),
            ))

        logger.info("Saved daily inspection for date %s successfully", date_str)
        return True, f"Đã lưu dữ liệu kiểm tra ngày {date_str} thành công."
    except Exception as exc:
        logger.error("Failed to save daily inspection for %s: %s", date_str, exc)
        return False, f"Lỗi lưu dữ liệu kiểm tra: {exc}"


def load_daily_inspection(
    date_str: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Loads daily inspection data from SQLite for a specific date.
    Returns None if no records exist for that date.
    """
    try:
        with db_session(db_path) as conn:
            cursor = conn.cursor()

            # Check if any inspection records exist for this date
            cursor.execute(
                "SELECT item_name, time_slot, status FROM daily_inspection WHERE check_date = ?;",
                (date_str,)
            )
            rows = cursor.fetchall()
            if not rows:
                return None

            items_data: Dict[str, Dict[str, str]] = {}
            inspectors_data: Dict[str, str] = {}

            for r in rows:
                item_name = r["item_name"]
                slot = r["time_slot"]
                val = r["status"]
                if item_name == "Inspected by":
                    inspectors_data[slot] = val
                else:
                    if item_name not in items_data:
                        items_data[item_name] = {}
                    items_data[item_name][slot] = val

            # Load meta
            cursor.execute(
                "SELECT * FROM daily_inspection_meta WHERE check_date = ?;",
                (date_str,)
            )
            meta_row = cursor.fetchone()
            remarks = {
                "shift1": meta_row["remark_shift1"] if meta_row else "",
                "shift2": meta_row["remark_shift2"] if meta_row else "",
            }
            details = {
                "shift1": meta_row["details_shift1"] if meta_row else "",
                "shift2": meta_row["details_shift2"] if meta_row else "",
            }

            return {
                "date": date_str,
                "items": items_data,
                "inspectors": inspectors_data,
                "remarks": remarks,
                "details": details,
            }
    except Exception as exc:
        logger.error("Failed to load daily inspection for %s: %s", date_str, exc)
        return None


def export_daily_inspection_to_excel(
    date_str: str,
    data: Dict[str, Any],
    filepath: Optional[Union[str, Path]] = None,
) -> Tuple[bool, str]:
    """
    Appends or updates a sheet named 'DD-MM-YYYY' inside the monthly master file
    'Daily inspection <MM-YYYY>.xlsx' matching Image 4 layout and styling.
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        logger.error("openpyxl is not installed.")
        return False, "Thư viện 'openpyxl' chưa được cài đặt."

    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
    except Exception:
        dt = datetime.now()

    target_path = Path(filepath) if filepath else get_daily_inspection_master_path(dt)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    sheet_name = get_daily_sheet_name(dt)

    try:
        if target_path.exists():
            wb = openpyxl.load_workbook(target_path)
        else:
            wb = openpyxl.Workbook()

        if sheet_name in wb.sheetnames:
            del wb[sheet_name]

        ws = wb.create_sheet(title=sheet_name)

        if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
            del wb["Sheet"]

        # ── 1. Column Widths ──
        ws.column_dimensions["A"].width = 12
        ws.column_dimensions["B"].width = 22
        for hour, col_letter in HOUR_TO_COL.items():
            ws.column_dimensions[col_letter].width = 6.8

        # ── 2. Styles ──
        shift_header_font = Font(name="Calibri", size=11, bold=True)
        hour_header_font = Font(name="Calibri", size=10, bold=True)
        category_font = Font(name="Calibri", size=10, bold=True)
        item_font = Font(name="Calibri", size=10, bold=True)
        data_font = Font(name="Calibri", size=10)
        bold_data_font = Font(name="Calibri", size=10, bold=True)

        shift_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        hour_fill = PatternFill(start_color="FFF9E6", end_color="FFF9E6", fill_type="solid")

        thin_side = Side(style="thin", color="000000")
        thin_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Helper to apply border across an entire range
        def set_border_range(min_col: int, min_row: int, max_col: int, max_row: int) -> None:
            for r in range(min_row, max_row + 1):
                for c in range(min_col, max_col + 1):
                    ws.cell(row=r, column=c).border = thin_border

        # ── 3. Row 1: Shift Headers ──
        # 1st Shift: C1:N1
        ws.merge_cells("C1:N1")
        ws["C1"] = "1st Shift"
        ws["C1"].font = shift_header_font
        ws["C1"].alignment = center_align
        ws["C1"].fill = shift_fill
        set_border_range(3, 1, 14, 1)

        # 2nd Shift: O1:Z1
        ws.merge_cells("O1:Z1")
        ws["O1"] = "2nd Shift"
        ws["O1"].font = shift_header_font
        ws["O1"].alignment = center_align
        ws["O1"].fill = shift_fill
        set_border_range(15, 1, 26, 1)

        # ── 4. Row 2: Hourly Headers (C2 to Z2) ──
        for idx, hour in enumerate(ALL_HOURS):
            col_idx = 3 + idx
            cell = ws.cell(row=2, column=col_idx)
            cell.value = hour
            cell.font = hour_header_font
            cell.alignment = center_align
            cell.fill = hour_fill
            cell.border = thin_border

        # ── 5. Rows 3 to 30: Inspection Items ──
        items_map = data.get("items", {})

        for row_idx, category, item_name, _ in INSPECTION_ITEMS:
            # Col B item label
            cell_b = ws[f"B{row_idx}"]
            cell_b.value = item_name
            cell_b.font = item_font
            cell_b.alignment = left_align
            cell_b.border = thin_border

            # Values for 24 hours (Cols C to Z)
            item_vals = items_map.get(item_name, {})
            for idx, hour in enumerate(ALL_HOURS):
                col_idx = 3 + idx
                c_cell = ws.cell(row=row_idx, column=col_idx)
                val = item_vals.get(hour, "")
                c_cell.value = val
                c_cell.font = bold_data_font if val in ("V", "X") else data_font
                c_cell.alignment = center_align
                c_cell.border = thin_border

        # Merge category blocks in Column A & B
        # Temp (°C): A3:B3 merged
        ws.merge_cells("A3:B3")
        ws["A3"] = "Temp (°C)"
        ws["A3"].font = item_font
        ws["A3"].alignment = center_align
        set_border_range(1, 3, 2, 3)

        # Humidity(%): A4:B4 merged
        ws.merge_cells("A4:B4")
        ws["A4"] = "Humidity(%)"
        ws["A4"].font = item_font
        ws["A4"].alignment = center_align
        set_border_range(1, 4, 2, 4)

        # Server: A5:A8
        ws.merge_cells("A5:A8")
        ws["A5"] = "Server"
        ws["A5"].font = category_font
        ws["A5"].alignment = center_align
        set_border_range(1, 5, 1, 8)

        # Storage: A9:A10
        ws.merge_cells("A9:A10")
        ws["A9"] = "Storage"
        ws["A9"].font = category_font
        ws["A9"].alignment = center_align
        set_border_range(1, 9, 1, 10)

        # Back-up devices: A11:B11 merged
        ws.merge_cells("A11:B11")
        ws["A11"] = "Back-up devices"
        ws["A11"].font = item_font
        ws["A11"].alignment = center_align
        set_border_range(1, 11, 2, 11)

        # Network: A12:A21
        ws.merge_cells("A12:A21")
        ws["A12"] = "Network"
        ws["A12"].font = category_font
        ws["A12"].alignment = center_align
        set_border_range(1, 12, 1, 21)

        # UPS: A22:A24
        ws.merge_cells("A22:A24")
        ws["A22"] = "UPS"
        ws["A22"].font = category_font
        ws["A22"].alignment = center_align
        set_border_range(1, 22, 1, 24)

        # Air condition: A25:A26
        ws.merge_cells("A25:A26")
        ws["A25"] = "Air\ncondition"
        ws["A25"].font = category_font
        ws["A25"].alignment = center_align
        set_border_range(1, 25, 1, 26)

        # Fire, Water leaks: A27:B27 merged
        ws.merge_cells("A27:B27")
        ws["A27"] = "Fire, Water leaks"
        ws["A27"].font = item_font
        ws["A27"].alignment = center_align
        set_border_range(1, 27, 2, 27)

        # Fire extinguisher: A28:B28 merged
        ws.merge_cells("A28:B28")
        ws["A28"] = "Fire extinguisher"
        ws["A28"].font = item_font
        ws["A28"].alignment = center_align
        set_border_range(1, 28, 2, 28)

        # Man IN-OUT: A29:B29 merged
        ws.merge_cells("A29:B29")
        ws["A29"] = "Man IN-OUT"
        ws["A29"].font = item_font
        ws["A29"].alignment = center_align
        set_border_range(1, 29, 2, 29)

        # Locks (doors & windows): A30:B30 merged
        ws.merge_cells("A30:B30")
        ws["A30"] = "Locks (doors & windows)"
        ws["A30"].font = item_font
        ws["A30"].alignment = center_align
        set_border_range(1, 30, 2, 30)

        # ── 6. Row 31: Inspected by ──
        ws.merge_cells("A31:B31")
        ws["A31"] = "Inspected by"
        ws["A31"].font = item_font
        ws["A31"].alignment = center_align
        set_border_range(1, 31, 2, 31)

        inspectors = data.get("inspectors", {})
        for idx, hour in enumerate(ALL_HOURS):
            col_idx = 3 + idx
            cell = ws.cell(row=31, column=col_idx)
            cell.value = inspectors.get(hour, "")
            cell.font = data_font
            cell.alignment = center_align
            cell.border = thin_border

        # ── 7. Row 32: Remarks ──
        ws.merge_cells("A32:B32")
        ws["A32"] = "Remarks"
        ws["A32"].font = item_font
        ws["A32"].alignment = center_align
        set_border_range(1, 32, 2, 32)

        remarks = data.get("remarks", {})
        # Shift 1: C32:N32
        ws.merge_cells("C32:N32")
        ws["C32"] = remarks.get("shift1", "")
        ws["C32"].font = data_font
        ws["C32"].alignment = left_align
        set_border_range(3, 32, 14, 32)

        # Shift 2: O32:Z32
        ws.merge_cells("O32:Z32")
        ws["O32"] = remarks.get("shift2", "")
        ws["O32"].font = data_font
        ws["O32"].alignment = left_align
        set_border_range(15, 32, 26, 32)

        # ── 8. Row 33: Inspection Details ──
        ws.merge_cells("A33:B33")
        ws["A33"] = "Inspection Details"
        ws["A33"].font = item_font
        ws["A33"].alignment = center_align
        set_border_range(1, 33, 2, 33)

        details = data.get("details", {})
        # Shift 1: C33:N33
        ws.merge_cells("C33:N33")
        ws["C33"] = details.get("shift1", "")
        ws["C33"].font = data_font
        ws["C33"].alignment = left_align
        set_border_range(3, 33, 14, 33)

        # Shift 2: O33:Z33
        ws.merge_cells("O33:Z33")
        ws["O33"] = details.get("shift2", "")
        ws["O33"].font = data_font
        ws["O33"].alignment = left_align
        set_border_range(15, 33, 26, 33)

        # ── 9. Rows 34-35: Legend (Below Table) ──
        ws["A34"] = "V : Normal"
        ws["A34"].font = bold_data_font

        ws["A35"] = "X : Abnormal"
        ws["A35"].font = bold_data_font

        # Save workbook to disk
        wb.save(target_path)
        logger.info("Successfully exported Daily inspection tab '%s' into %s", sheet_name, target_path)
        return True, f"Đã xuất thành công tab [{sheet_name}] vào file:\n{target_path}"

    except PermissionError:
        logger.error("Permission denied when writing to %s (file may be open).", target_path)
        return False, f"Không thể ghi file vì file Excel đang được mở:\n{target_path}\nVui lòng đóng file Excel và thử lại."
    except Exception as exc:
        logger.error("Failed to export daily inspection: %s", exc)
        return False, f"Lỗi xuất file Daily inspection: {exc}"
