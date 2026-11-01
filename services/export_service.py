"""
Shift Report Excel Export Service.

Generates polished shift reports matching the exact layout of Image 1 & 2.
Appends or updates tabs named 'DD-Mon-YYYY (Shift 1/2)' inside the master
monthly workbook: D:\\Report\\<YYYY>\\<Month>\\Shift report <MM-YYYY>.xlsx.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import logging

from config.settings import get_app_dir

logger = logging.getLogger(__name__)


def get_default_report_dir(dt: Optional[datetime] = None) -> Path:
    """
    Returns the target monthly directory: D:\\Report\\<YYYY>\\<Month>
    Falls back to <app_dir>\\Report\\<YYYY>\\<Month> if drive D: is not accessible.
    """
    date_obj = dt or datetime.now()
    year_str = date_obj.strftime("%Y")
    month_name = date_obj.strftime("%b")  # e.g. "Oct", "Nov"

    base_root = Path("D:/Report") if Path("D:/").exists() else (get_app_dir() / "Report")
    return base_root / year_str / month_name


def get_shift_report_master_path(dt: Optional[datetime] = None) -> Path:
    """
    Returns the full path to the monthly Shift report master workbook.
    Example: D:\\Report\\2026\\Oct\\Shift report 10-2026.xlsx
    """
    date_obj = dt or datetime.now()
    folder = get_default_report_dir(date_obj)
    filename = f"Shift report {date_obj.strftime('%m-%Y')}.xlsx"
    return folder / filename


def get_sheet_tab_name(dt: datetime, shift: str) -> str:
    """
    Generates standardized tab name matching Image 2:
    Example: '29-Oct-2026 (Shift 1)' or '29-Oct-2026 (Shift 2)'.
    """
    shift_tag = "Shift 1" if ("1" in shift or "Ngày" in shift or "Day" in shift) else "Shift 2"
    return f"{dt.strftime('%d-%b-%Y')} ({shift_tag})"


def export_shift_report_to_excel(
    filepath: Optional[Union[str, Path]] = None,
    dept: str = "IT",
    section: str = "Dx Engineering Team",
    prepared_by: str = "",
    group: str = "B",
    shift: str = "Ca Ngày",
    date_val: Optional[Union[str, datetime]] = None,
    incidents: Optional[List[Dict[str, Any]]] = None,
    inspection_data: Optional[Dict[str, str]] = None,
    hmi_data: Optional[Dict[str, Dict[str, str]]] = None,
) -> Tuple[bool, str]:
    """
    Appends or updates a shift report sheet in the monthly master workbook.
    Layout precisely matches Images 1 & 2.
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        logger.error("openpyxl library is not installed.")
        return False, "Thư viện 'openpyxl' chưa được cài đặt. Vui lòng cài đặt: pip install openpyxl"

    # Resolve date
    if isinstance(date_val, datetime):
        dt = date_val
    elif isinstance(date_val, str) and date_val.strip():
        try:
            dt = datetime.strptime(date_val[:10], "%Y-%m-%d")
        except Exception:
            dt = datetime.now()
    else:
        dt = datetime.now()

    # Resolve master workbook path
    target_path = Path(filepath) if filepath else get_shift_report_master_path(dt)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    sheet_name = get_sheet_tab_name(dt, shift)

    try:
        # Load existing workbook or create a new one
        if target_path.exists():
            wb = openpyxl.load_workbook(target_path)
        else:
            wb = openpyxl.Workbook()

        # If sheet tab exists, delete it so we write fresh
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]

        ws = wb.create_sheet(title=sheet_name)

        # Remove default empty "Sheet" if other sheets exist
        if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
            del wb["Sheet"]

        # ── 1. Column Widths Matching Images ──
        column_widths = {
            "A": 4, "B": 18, "C": 28, "D": 12, "E": 18,
            "F": 14, "G": 28, "H": 18, "I": 16, "J": 8
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # ── 2. Styles & Palettes ──
        title_font = Font(name="Calibri", size=18, bold=True)
        subtitle_font = Font(name="Calibri", size=11, bold=True)
        bold_font = Font(name="Calibri", size=11, bold=True)
        normal_font = Font(name="Calibri", size=11)
        header_fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
        thin_side = Side(style="thin")
        thin_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="top", wrap_text=True)

        def apply_row_borders(row_idx: int, cols: List[str] = None) -> None:
            for col in (cols or ["B", "C", "D", "E", "F", "G", "H", "I"]):
                ws[f"{col}{row_idx}"].border = thin_border

        def set_inspection_row(row_idx: int, label: str, value: str = "") -> None:
            """Formats standard inspection row with labels, borders, and status value."""
            ws[f"C{row_idx}"] = label
            ws[f"C{row_idx}"].font = bold_font
            ws[f"C{row_idx}"].fill = header_fill
            ws[f"C{row_idx}"].border = thin_border
            ws[f"H{row_idx}"] = value
            ws[f"H{row_idx}"].font = normal_font
            ws[f"H{row_idx}"].border = thin_border
            for col in ["B", "D", "E", "F", "G", "I"]:
                ws[f"{col}{row_idx}"].border = thin_border

        def make_section_header(cell_range: str, text: str) -> None:
            ws.merge_cells(cell_range)
            first_cell = cell_range.split(":")[0]
            ws[first_cell] = text
            ws[first_cell].font = bold_font
            ws[first_cell].fill = header_fill
            ws[first_cell].alignment = center_align
            ws[first_cell].border = thin_border

        # ── 3. Header Section (Rows 1-5) Matching Image 1 ──
        # Title & Date in Col E:F
        ws.merge_cells("E1:G1")
        ws["E1"] = "Shift Report"
        ws["E1"].font = title_font
        ws["E1"].alignment = center_align

        ws.merge_cells("E2:G2")
        ws["E2"] = f"({dt.strftime('%d-%b-%Y')})"
        ws["E2"].font = subtitle_font
        ws["E2"].alignment = center_align

        # Metadata Left
        ws["B2"] = f"Dept.: {dept}"
        ws["B2"].font = bold_font

        ws["B3"] = f"Sect.: {section}"
        ws["B3"].font = bold_font

        ws["B4"] = f"Prepared by: {prepared_by}"
        ws["B4"].font = bold_font

        ws["B5"] = f"Group:\t{group}"
        ws["B5"].font = bold_font

        # ── 4. General Task Description (Rows 6-18) ──
        ws.merge_cells("B6:I18")
        ws["B6"] = (
            "1. General Task Description:\n"
            "- Make a roll call of the computer room\n"
            "- Monitor status lights of Hardware Attention and Fault\n"
            "- Monitoring for Servers, Switch, Router, MES PC, MES Printer\n"
            "- Report after shift about status and any problem in Shift\n"
            "- Check Eviroment and all equipments in Server Room\n"
            "- Stop/Start Server and equipment when PoscoCenter order.\n"
            "- Check equipment 2hours/time and Clean equipment 01 time/month\n"
            "- Managing:\n"
            " + Restore and backup OS System\n"
            " + Hardware error\n"
            " + Visistor\n"
            " + Equipment In/out\n"
            "- Improve IT Device in IT Room (Server, UPS)\n"
            "- Control equipment in IT Warehouse in Server Room."
        )
        ws["B6"].alignment = left_align
        ws["B6"].font = normal_font

        # ── 5. "2. Detail" (Row 19) ──
        ws["B19"] = "2. Detail"
        ws["B19"].font = bold_font

        # ── 6. Detail Headers (Row 20) ──
        ws.merge_cells("B20:C20")
        detail_headers = {
            "B": "Category", "D": "Time", "E": "Failure", "F": "Reason",
            "G": "Solution", "H": "Current Situation", "I": "Contact Number"
        }
        for col, text in detail_headers.items():
            cell = ws[f"{col}20"]
            cell.value = text
            cell.font = bold_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border
        ws["C20"].border = thin_border
        ws["C20"].fill = header_fill

        # ── 7. Detail Data Rows (Rows 21-39) Matching Image 1 ──
        env_data = inspection_data or {}

        # Rows 21-22: Indoor Environment
        make_section_header("B21:B22", "Indoor\nEnvironment")
        set_inspection_row(21, "Standard Temperature (19 – 25)", env_data.get("temperature", "22 °C"))
        set_inspection_row(22, "Standard Humidity (35 – 55)", env_data.get("humidity", "46%"))

        # Rows 23-31: H/W Inspection
        make_section_header("B23:B31", "H/W Inspection")
        hw_items = [
            (23, "MES Server"),
            (24, "CLTS Server"),
            (25, "HMI Server"),
            (26, "MES PC"),
            (27, "CLTS PC"),
            (28, "HMI PC"),
            (29, "MES Printer"),
            (30, "Storage"),
            (31, "Network"),
        ]
        for row_idx, item_name in hw_items:
            set_inspection_row(row_idx, item_name, env_data.get(item_name, "Running normal"))

        # Rows 32-35: Facility Inspection
        make_section_header("B32:B35", "Facility\nInspection")
        facility_items = [
            (32, "UPS", "Running normal"),
            (33, "Air conditioning", "Running normal"),
            (34, "Fire, leaks", "None"),
            (35, "Fire extinguisher", "OK"),
        ]
        for row_idx, item_name, default_val in facility_items:
            set_inspection_row(row_idx, item_name, env_data.get(item_name, default_val))

        # Row 36: Security Inspection
        ws["B36"] = "Security\nInspection"
        ws["B36"].font = bold_font
        ws["B36"].fill = header_fill
        ws["B36"].alignment = center_align
        ws["B36"].border = thin_border
        set_inspection_row(36, "Locks (doors & windows)", env_data.get("Locks (doors & windows)", "OK"))

        # Row 37: MES Server Backup
        ws.merge_cells("B37:C37")
        ws["B37"] = "MES Server Backup"
        ws["B37"].font = bold_font
        ws["B37"].fill = header_fill
        ws["B37"].border = thin_border
        ws["C37"].border = thin_border
        ws["H37"] = env_data.get("MES Server Backup", "OK")
        ws["H37"].font = normal_font
        apply_row_borders(37)

        # Row 38: MES Application
        ws.merge_cells("B38:C38")
        ws["B38"] = "MES Application"
        ws["B38"].font = bold_font
        ws["B38"].fill = header_fill
        ws["B38"].border = thin_border
        ws["C38"].border = thin_border
        ws["H38"] = env_data.get("MES Application", "OK")
        ws["H38"].font = normal_font
        apply_row_borders(38)

        # Row 39: Remark
        ws.merge_cells("B39:C39")
        ws["B39"] = "Remark"
        ws["B39"].font = bold_font
        ws["B39"].fill = header_fill
        ws["B39"].border = thin_border
        ws["C39"].border = thin_border
        ws["D39"] = env_data.get("Remark_detail", "")
        ws["D39"].font = normal_font
        ws["H39"] = env_data.get("Remark", "OK")
        ws["H39"].font = normal_font
        apply_row_borders(39)

        # Map incident records into Rows 21-39
        if incidents:
            item_row_map = {
                "Standard Temperature (19 – 25)": 21, "Standard Humidity (35 – 55)": 22,
                "MES Server": 23, "CLTS Server": 24, "HMI Server": 25, "MES PC": 26,
                "CLTS PC": 27, "HMI PC": 28, "MES Printer": 29, "Storage": 30, "Network": 31,
                "UPS": 32, "Air conditioning": 33, "Fire, leaks": 34, "Fire extinguisher": 35,
                "Locks (doors & windows)": 36, "MES Server Backup": 37, "MES Application": 38,
                "Remark": 39, "Remark / Other Issue": 39,
            }
            cat_row_map = {
                "Indoor Environment": 21, "H/W Inspection": 23, "Facility Inspection": 32,
                "Security Inspection": 36, "MES Server Backup": 37, "MES Application": 38,
                "Remark / Other Issue": 39,
            }

            for inc in incidents:
                sub = inc.get("sub_category", "")
                cat = inc.get("category", "")
                target_row = item_row_map.get(sub) or cat_row_map.get(cat, 39)

                # Time: only time portion if datetime provided
                time_str = inc.get("time", "")
                if len(time_str) >= 16:
                    time_val = time_str[11:16]
                else:
                    time_val = time_str

                col_data = {
                    "D": time_val,
                    "E": inc.get("failure", ""),
                    "F": inc.get("reason", ""),
                    "G": inc.get("solution", ""),
                    "H": inc.get("current_situation", "Running normal"),
                    "I": inc.get("contact", ""),
                }

                for col_letter, val in col_data.items():
                    cell = ws[f"{col_letter}{target_row}"]
                    old_val = str(cell.value) if cell.value is not None else ""
                    if old_val and val:
                        cell.value = f"{old_val}\n{val}"
                    elif val:
                        cell.value = str(val)

                    cell.font = normal_font
                    cell.border = thin_border
                    cell.alignment = center_align

        # ── 8. "3. HMI checking" (Rows 41-48) Matching Image 2 ──
        # Title Boxed: Row 41
        ws.merge_cells("B41:H41")
        ws["B41"] = "3. HMI checking"
        ws["B41"].font = Font(name="Calibri", size=14, bold=True)
        ws["B41"].alignment = center_align
        for col_l in ["B", "C", "D", "E", "F", "G", "H"]:
            ws[f"{col_l}41"].border = thin_border

        # Headers: Row 42
        ws["B42"] = "Line"
        ws["B42"].font = bold_font
        ws["B42"].fill = header_fill
        ws["B42"].alignment = center_align
        ws["B42"].border = thin_border

        ws["C42"] = "MES link SCC"
        ws["C42"].font = bold_font
        ws["C42"].fill = header_fill
        ws["C42"].alignment = center_align
        ws["C42"].border = thin_border

        ws["D42"] = "SCC Link PLC"
        ws["D42"].font = bold_font
        ws["D42"].fill = header_fill
        ws["D42"].alignment = center_align
        ws["D42"].border = thin_border

        # Merge E42:F42 for Application Link
        ws.merge_cells("E42:F42")
        ws["E42"] = "Application Link"
        ws["E42"].font = bold_font
        ws["E42"].fill = header_fill
        ws["E42"].alignment = center_align
        ws["E42"].border = thin_border
        ws["F42"].border = thin_border

        # Merge G42:H42 for Remark
        ws.merge_cells("G42:H42")
        ws["G42"] = "Remark"
        ws["G42"].font = bold_font
        ws["G42"].fill = header_fill
        ws["G42"].alignment = center_align
        ws["G42"].border = thin_border
        ws["H42"].border = thin_border

        # Lines PCM -> CLTS: Rows 43-48
        hmi_lines = ["PCM", "CAL", "FH-RCL", "CR-RCL", "PDS", "CLTS"]
        for idx, line in enumerate(hmi_lines):
            row_num = 43 + idx
            line_data = (hmi_data or {}).get(line, {})

            ws[f"B{row_num}"] = line
            ws[f"B{row_num}"].font = normal_font
            ws[f"B{row_num}"].border = thin_border
            ws[f"B{row_num}"].alignment = center_align

            ws[f"C{row_num}"] = line_data.get("MES link SCC", "OK")
            ws[f"C{row_num}"].font = normal_font
            ws[f"C{row_num}"].border = thin_border
            ws[f"C{row_num}"].alignment = center_align

            ws[f"D{row_num}"] = line_data.get("SCC Link PLC", "OK")
            ws[f"D{row_num}"].font = normal_font
            ws[f"D{row_num}"].border = thin_border
            ws[f"D{row_num}"].alignment = center_align

            # E:F merged
            ws.merge_cells(f"E{row_num}:F{row_num}")
            ws[f"E{row_num}"] = line_data.get("Application Link", "OK")
            ws[f"E{row_num}"].font = normal_font
            ws[f"E{row_num}"].border = thin_border
            ws[f"F{row_num}"].border = thin_border
            ws[f"E{row_num}"].alignment = center_align

            # G:H merged
            ws.merge_cells(f"G{row_num}:H{row_num}")
            ws[f"G{row_num}"] = line_data.get("Remark", "")
            ws[f"G{row_num}"].font = normal_font
            ws[f"G{row_num}"].border = thin_border
            ws[f"H{row_num}"].border = thin_border
            ws[f"G{row_num}"].alignment = left_align

        # Save workbook to disk
        wb.save(target_path)
        logger.info("Successfully exported tab '%s' into %s", sheet_name, target_path)
        return True, f"Đã xuất thành công tab [{sheet_name}] vào file:\n{target_path}"

    except PermissionError:
        logger.error("Permission denied when writing to %s (file may be open).", target_path)
        return False, f"Không thể ghi file vì file Excel đang được mở:\n{target_path}\nVui lòng đóng file Excel và thử lại."
    except Exception as exc:
        logger.error("Failed to export shift report: %s", exc)
        return False, f"Lỗi xuất báo cáo Shift report: {exc}"
