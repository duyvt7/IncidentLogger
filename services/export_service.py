"""
Shift Report Excel Export Service.

Generates polished shift reports matching the Shift_Report_Full_Format.xlsx layout
using openpyxl, cleanly decoupled from the database and UI layers.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def export_shift_report_to_excel(
    filepath: Union[str, Path],
    dept: str = "IT",
    section: str = "IT Management",
    prepared_by: str = "",
    group: str = "",
    shift: str = "",
    incidents: Optional[List[Dict[str, Any]]] = None,
    inspection_data: Optional[Dict[str, str]] = None,
    hmi_data: Optional[Dict[str, Dict[str, str]]] = None,
) -> Tuple[bool, str]:
    """
    Exports shift report data to an Excel file with full layout styling.
    
    Args:
        filepath: Target destination file path.
        dept: Department name.
        section: Section name.
        prepared_by: Name of the person preparing the report.
        group: Group/team name.
        shift: Shift description (Day Shift / Night Shift).
        incidents: List of incident dictionaries.
        inspection_data: Dictionary of daily inspection readings.
        hmi_data: Dictionary of HMI line status checks.
        
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        logger.error("openpyxl library is not installed.")
        return False, "Thư viện 'openpyxl' chưa được cài đặt. Vui lòng cài đặt: pip install openpyxl"

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Shift Report"

        # 1. Thiết lập độ rộng cột chuẩn
        column_widths = {
            "A": 5, "B": 19, "C": 29, "D": 12, "E": 15,
            "F": 12, "G": 25, "H": 20, "I": 16, "J": 20
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # 2. Định nghĩa typography & styles
        header_font = Font(name="Calibri", size=14, bold=True)
        bold_font = Font(name="Calibri", size=11, bold=True)
        normal_font = Font(name="Calibri", size=11)
        header_fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
        thin_border = Border(
            left=Side(style="thin"), right=Side(style="thin"),
            top=Side(style="thin"), bottom=Side(style="thin")
        )
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="top", wrap_text=True)

        # ── Row 1-5: Header ──
        ws.merge_cells("B1:C1")
        ws.merge_cells("E1:J3")
        ws["E1"] = "Shift Report"
        ws["E1"].font = header_font
        ws["E1"].alignment = center_align

        ws.merge_cells("B2:C2")
        ws["B2"] = f"Dept.: {dept}"
        ws["B2"].alignment = Alignment(horizontal="left")

        ws.merge_cells("B3:C3")
        ws["B3"] = f"Sect.: {section}"
        ws["B3"].alignment = Alignment(horizontal="left")

        ws["B4"] = f"Prepared by: {prepared_by}"
        ws["B5"] = f"Group: {group}"

        # ── Row 6-18: 1. General Task Description ──
        ws.merge_cells("B6:J18")
        ws["B6"] = (
            "1. General Task Description:\n"
            "- Make a roll call of the computer room\n"
            "- Monitor status lights of Hardware Attention and Fault\n"
            "- Monitoring for Servers, Switch, Router, MES PC, MES Printer\n"
            "- Report after shift about status and any problem in Shift\n"
            "- Check Environment and all equipments in Server Room\n"
            "- Stop/Start Server and equipment when PoscoCenter order\n"
            "- Check equipment 2hours/time and Clean equipment 01 time/month\n"
            "- Managing\n"
            "+ Restore and backup OS System\n"
            "+ Hardware error\n"
            "+ Visitor\n"
            "+ Equipment In/out\n"
            "+ Improve IT Device in IT Room (Server, UPS)\n"
            "+ Control equipment in IT Warehouse in Server Room."
        )
        ws["B6"].alignment = left_align
        ws["B6"].font = normal_font

        # ── Row 20: 2. Detail Header ──
        ws.merge_cells("B20:J20")
        ws["B20"] = "2. Detail"
        ws["B20"].font = bold_font

        # ── Row 21: Detail Table Headers ──
        detail_headers = {
            "B": "Category", "D": "Time", "E": "Failure", "F": "Reason",
            "G": "Solution", "H": "Current Situation", "I": "Contact Number"
        }
        ws.merge_cells("B21:C21")
        for col, text in detail_headers.items():
            cell = ws[f"{col}21"]
            cell.value = text
            cell.font = bold_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border
        ws["C21"].border = thin_border
        ws["C21"].fill = header_fill

        def set_inspection_row(row_idx: int, label: str, value: str = "") -> None:
            """Formats standard inspection row with labels, borders, and status value."""
            ws[f"C{row_idx}"] = label
            ws[f"C{row_idx}"].font = bold_font
            ws[f"C{row_idx}"].fill = header_fill
            ws[f"C{row_idx}"].border = thin_border
            ws[f"H{row_idx}"] = value
            ws[f"H{row_idx}"].font = normal_font
            ws[f"H{row_idx}"].border = thin_border
            for col in ["D", "E", "F", "G", "I"]:
                ws[f"{col}{row_idx}"].border = thin_border

        def make_section_header(cell_range: str, text: str) -> None:
            ws.merge_cells(cell_range)
            first_cell = cell_range.split(":")[0]
            ws[first_cell] = text
            ws[first_cell].font = bold_font
            ws[first_cell].fill = header_fill
            ws[first_cell].alignment = center_align
            ws[first_cell].border = thin_border

        # ── Row 22-23: Indoor Environment ──
        make_section_header("B22:B23", "Indoor Environment")
        env_data = inspection_data or {}
        set_inspection_row(22, "Standard Temperature (19 - 25)", env_data.get("temperature", "22℃"))
        set_inspection_row(23, "Standard Humidity (35 - 55)", env_data.get("humidity", "46%"))

        # ── Row 24-32: H/W Inspection ──
        make_section_header("B24:B32", "H/W Inspection")
        hw_items = [
            "MES Server", "CLTS Server", "HMI Server", "MES PC",
            "CLTS PC", "HMI PC", "MES Printer", "Storage", "Network"
        ]
        for i, item in enumerate(hw_items):
            set_inspection_row(24 + i, item, env_data.get(item, "Running normal"))

        # ── Row 33-36: Facility Inspection ──
        make_section_header("B33:B36", "Facility Inspection")
        facility_items = [
            (33, "UPS", "Running normal"),
            (34, "Air conditioning", "None"),
            (35, "Fire, leaks", "OK"),
            (36, "Fire extinguisher", "OK"),
        ]
        for row_n, label, default_val in facility_items:
            set_inspection_row(row_n, label, env_data.get(label, default_val))

        # ── Row 37: Security Inspection ──
        ws["B37"] = "Security Inspection"
        ws["B37"].font = bold_font
        ws["B37"].fill = header_fill
        ws["B37"].border = thin_border
        set_inspection_row(37, "Locks (doors & windows)", env_data.get("Locks (doors & windows)", "OK"))

        # ── Row 38: MES Server Backup ──
        ws.merge_cells("B38:C38")
        ws["B38"] = "MES Server Backup"
        ws["B38"].font = bold_font
        ws["B38"].fill = header_fill
        ws["B38"].border = thin_border
        ws["C38"].border = thin_border
        ws["H38"] = env_data.get("MES Server Backup", "OK")
        ws["H38"].border = thin_border
        for c in ["D", "E", "F", "G", "I"]:
            ws[f"{c}38"].border = thin_border

        # ── Row 39: MES Application ──
        ws.merge_cells("B39:C39")
        ws["B39"] = "MES Application"
        ws["B39"].font = bold_font
        ws["B39"].fill = header_fill
        ws["B39"].border = thin_border
        ws["C39"].border = thin_border
        ws["H39"] = env_data.get("MES Application", "OK")
        ws["H39"].border = thin_border
        for c in ["D", "E", "F", "G", "I"]:
            ws[f"{c}39"].border = thin_border

        # ── Row 40: Remark / Other Issue ──
        ws.merge_cells("B40:C40")
        ws["B40"] = "Remark / Other Issue"
        ws["B40"].font = bold_font
        ws["B40"].fill = header_fill
        ws["B40"].border = thin_border
        ws["C40"].border = thin_border
        for c in ["D", "E", "F", "G", "H", "I"]:
            ws[f"{c}40"].border = thin_border

        # ── Map and write Incidents into Rows 22-40 ──
        if incidents:
            item_map = {
                "Standard Temperature (19 - 25)": 22, "Standard Humidity (35 - 55)": 23,
                "MES Server": 24, "CLTS Server": 25, "HMI Server": 26, "MES PC": 27,
                "CLTS PC": 28, "HMI PC": 29, "MES Printer": 30, "Storage": 31, "Network": 32,
                "UPS": 33, "Air conditioning": 34, "Fire, leaks": 35, "Fire extinguisher": 36,
                "Locks (doors & windows)": 37, "MES Server Backup": 38, "MES Application": 39,
                "Remark / Other Issue": 40,
            }
            cat_map = {
                "Indoor Environment": 22, "H/W Inspection": 24, "Facility Inspection": 33,
                "Security Inspection": 37, "MES Server Backup": 38, "MES Application": 39,
                "Remark / Other Issue": 40,
            }

            for inc in incidents:
                cat = inc.get("category", "")
                sub = inc.get("sub_category", "")
                target_row = item_map.get(sub) or cat_map.get(cat, 40)

                col_data = {
                    "D": inc.get("time", ""),
                    "E": inc.get("failure", ""),
                    "F": inc.get("reason", ""),
                    "G": inc.get("solution", ""),
                    "H": inc.get("current_situation", ""),
                    "I": inc.get("contact", ""),
                }

                for col, val in col_data.items():
                    cell = ws[f"{col}{target_row}"]
                    old_val = str(cell.value) if cell.value is not None else ""
                    if old_val:
                        cell.value = old_val + "\n" + str(val)
                    else:
                        cell.value = str(val)

                    cell.font = normal_font
                    cell.border = thin_border
                    cell.alignment = center_align

        # ── Row 42: 3. HMI checking ──
        ws.merge_cells("B42:J42")
        ws["B42"] = "3. HMI checking"
        ws["B42"].font = bold_font

        hmi_header_row = 43
        hmi_headers = {
            "B": "Line", "C": "MES link SCC", "D": "SCC Link PLC",
            "E": "Application Link", "F": "Remark"
        }
        for col, text in hmi_headers.items():
            cell = ws[f"{col}{hmi_header_row}"]
            cell.value = text
            cell.font = bold_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        hmi_lines = ["PCM", "CAL", "FH-RCL", "CR-RCL", "PDS", "CLTS"]
        for i, line in enumerate(hmi_lines):
            row_n = hmi_header_row + 1 + i
            ws[f"B{row_n}"] = line
            ws[f"B{row_n}"].font = normal_font
            ws[f"B{row_n}"].border = thin_border
            for c in ["C", "D", "E", "F"]:
                ws[f"{c}{row_n}"].border = thin_border
                if hmi_data and line in hmi_data:
                    col_map = {
                        "C": "MES link SCC",
                        "D": "SCC Link PLC",
                        "E": "Application Link",
                        "F": "Remark",
                    }
                    ws[f"{c}{row_n}"] = hmi_data[line].get(col_map[c], "")
                    ws[f"{c}{row_n}"].font = normal_font

        # 3. Ghi file ra đĩa
        target_path = Path(filepath)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(target_path)
        logger.info("Excel report exported successfully to: %s", target_path)
        return True, f"Đã xuất báo cáo Excel thành công: {target_path.name}"

    except PermissionError:
        logger.error("Permission denied when writing to %s (file may be open).", filepath)
        return False, "Không thể lưu file vì file đang được mở trong Excel. Vui lòng đóng file và thử lại."
    except Exception as exc:
        logger.error("Failed to export Excel report: %s", exc)
        return False, f"Lỗi khi xuất file Excel: {exc}"

