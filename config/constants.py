"""
Business Constants and UI Style Declarations.

Centralizes business categories, HMI checking lists, operator rosters,
color palettes, and typography.
"""
from typing import List, Tuple

# ── Incident Detail Category and Sub-category Hierarchy ──
DETAIL_STRUCTURE: List[Tuple[str, List[str]]] = [
    (
        "Indoor Environment",
        ["Standard Temperature (19 - 25)", "Standard Humidity (35 - 55)"],
    ),
    (
        "H/W Inspection",
        [
            "MES Server",
            "CLTS Server",
            "HMI Server",
            "MES PC",
            "CLTS PC",
            "HMI PC",
            "MES Printer",
            "Storage",
            "Network",
        ],
    ),
    (
        "Facility Inspection",
        ["UPS", "Air conditioning", "Fire, leaks", "Fire extinguisher"],
    ),
    (
        "Security Inspection",
        ["Locks (doors & windows)"],
    ),
    ("MES Server Backup", []),
    ("MES Application", []),
    ("Remark / Other Issue", []),
]

# ── HMI Monitoring Configuration ──
HMI_LINES: List[str] = ["PCM", "CAL", "FH-RCL", "CR-RCL", "PDS", "CLTS"]
HMI_COLS: List[str] = [
    "MES link SCC",
    "SCC Link PLC",
    "Application Link",
    "Remark",
]
HMI_STATUS_OPTIONS: List[str] = ["OK", "Stopped"]

# ── Incident Form Options ──
CURRENT_SITUATION_OPTIONS: List[str] = [
    "Running normal",
    "Đang xử lí",
    "Chờ hỗ trợ",
    "Cần theo dõi",
    "Tạm dừng",
]

# ── Shift and Operator Lists ──
DEFAULT_OPERATORS: List[str] = [
    "Hoàng Ngọc Huy",
    "Nguyễn Mai Nghĩa",
    "Vũ Thành Duy",
    "Võ Đình Thủy",
    "admin",
]

SHIFT_OPTIONS: List[str] = ["Ca Ngày", "Ca Đêm"]

# ── Color Palette ──
class Colors:
    """Modern flat color palette."""
    BG: str = "#F1F5F9"           # Slate-100 background
    CARD_BG: str = "#FFFFFF"      # White card surface
    BORDER: str = "#E2E8F0"       # Slate-200 border
    PRIMARY: str = "#6366F1"      # Indigo-500
    PRIMARY_HOVER: str = "#4F46E5"# Indigo-600
    TEXT_MAIN: str = "#1E293B"    # Slate-800 primary text
    TEXT_DIM: str = "#64748B"     # Slate-500 secondary text
    SUCCESS: str = "#10B981"      # Emerald-500
    DANGER: str = "#EF4444"       # Red-500
    WARNING: str = "#F59E0B"      # Amber-500
    HDR_BG: str = "#CCFFFF"       # Classic soft cyan header for excel & table
    SELECT_BG: str = "#C7D2FE"    # Indigo-200 selection highlight
    EXCEL_BTN: str = "#059669"    # Emerald-600 for Excel export button


# ── Typography / Fonts ──
class Fonts:
    """Standardized font specifications using Segoe UI."""
    MAIN: Tuple[str, int] = ("Segoe UI", 10)
    BOLD: Tuple[str, int, str] = ("Segoe UI", 10, "bold")
    TITLE: Tuple[str, int, str] = ("Segoe UI", 14, "bold")
    HEADER: Tuple[str, int, str] = ("Segoe UI", 18, "bold")
    SM: Tuple[str, int] = ("Segoe UI", 9)
    XS: Tuple[str, int] = ("Segoe UI", 8)
