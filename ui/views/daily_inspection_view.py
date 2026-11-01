"""
DailyInspectionView Component.

Interactive 24-hour IT Daily Inspection grid matching Image 4.
Allows 1-click default generation, click-to-toggle V/X health status,
SQLite persistence, and export to monthly master workbook:
D:\\Report\\<YYYY>\\<Month>\\Daily inspection <MM-YYYY>.xlsx
"""
from typing import Any, Callable, Dict, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry

from config.constants import Colors, Fonts
from services.daily_inspection_service import (
    ALL_HOURS,
    SHIFT_1_HOURS,
    SHIFT_2_HOURS,
    INSPECTION_ITEMS,
    generate_default_daily_data,
    save_daily_inspection,
    load_daily_inspection,
    export_daily_inspection_to_excel,
    get_daily_inspection_master_path,
    get_daily_sheet_name,
)

logger = logging.getLogger(__name__)


class DailyInspectionView(tk.Frame):
    """
    Daily Inspection 24H View with visual grid, toggle status, and Excel export.
    """

    def __init__(
        self,
        parent: tk.Widget,
        get_shift_info_cb: Optional[Callable[[], Dict[str, str]]] = None,
        **kwargs,
    ):
        super().__init__(parent, bg=Colors.BG, **kwargs)
        self.get_shift_info_cb = get_shift_info_cb

        # Key: (item_name, hour) -> widget (Label or Entry)
        self._cells: Dict[Tuple[str, str], Any] = {}
        # Key: hour -> Entry for inspector
        self._inspector_cells: Dict[str, tk.Entry] = {}
        # Meta entries for Remarks & Details
        self._remark_s1_entry: Optional[tk.Entry] = None
        self._remark_s2_entry: Optional[tk.Entry] = None
        self._details_s1_entry: Optional[tk.Entry] = None
        self._details_s2_entry: Optional[tk.Entry] = None

        self._build_ui()
        self.load_data_for_date()

    def _build_ui(self) -> None:
        """Constructs action bar, inspector control bar, scrollable grid, and status legend."""
        # ── 1. Top Action Bar ──
        action_bar = tk.Frame(
            self,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        action_bar.pack(fill="x", padx=12, pady=(10, 6))

        # Title
        tk.Label(
            action_bar,
            text="📋 4. Daily Inspection (24H)",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.TITLE,
        ).pack(side="left", padx=16, pady=10)

        # Action Buttons on Right
        tk.Button(
            action_bar,
            text="📤 Xuất Excel Daily Inspection",
            bg=Colors.EXCEL_BTN,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.export_excel,
        ).pack(side="right", padx=(4, 16), pady=8)

        tk.Button(
            action_bar,
            text="💾 Lưu Dữ Liệu",
            bg=Colors.SUCCESS,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.save_data,
        ).pack(side="right", padx=4, pady=8)

        tk.Button(
            action_bar,
            text="⚡ Tạo Mặc Định Hôm Nay",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.fill_default_data,
        ).pack(side="right", padx=4, pady=8)

        # ── 2. Filter & Date Bar ──
        filter_bar = tk.Frame(self, bg=Colors.BG)
        filter_bar.pack(fill="x", padx=12, pady=4)

        tk.Label(
            filter_bar,
            text="📅 Chọn Ngày Kiểm Tra:",
            bg=Colors.BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.BOLD,
        ).pack(side="left", padx=(4, 8))

        self.date_entry = DateEntry(
            filter_bar,
            width=12,
            background=Colors.PRIMARY,
            foreground="white",
            borderwidth=1,
            date_pattern="yyyy-mm-dd",
            font=Fonts.MAIN,
        )
        self.date_entry.pack(side="left", padx=4)
        self.date_entry.set_date(datetime.now())
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self.load_data_for_date())

        tk.Button(
            filter_bar,
            text="↺ Tải Lại",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.MAIN,
            relief="flat",
            padx=10,
            pady=2,
            cursor="hand2",
            command=self.load_data_for_date,
        ).pack(side="left", padx=8)

        # Quick inspector name inputs for Shift 1 & Shift 2
        tk.Label(
            filter_bar,
            text="👤 Người trực Ca 1:",
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.SM,
        ).pack(side="left", padx=(20, 4))

        self.entry_insp_s1 = tk.Entry(filter_bar, width=12, font=Fonts.MAIN)
        self.entry_insp_s1.insert(0, "Nghia")
        self.entry_insp_s1.pack(side="left", padx=4)

        tk.Label(
            filter_bar,
            text="👤 Người trực Ca 2:",
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.SM,
        ).pack(side="left", padx=(10, 4))

        self.entry_insp_s2 = tk.Entry(filter_bar, width=12, font=Fonts.MAIN)
        self.entry_insp_s2.insert(0, "Huy")
        self.entry_insp_s2.pack(side="left", padx=4)

        tk.Button(
            filter_bar,
            text="Áp dụng tên vào bảng",
            bg=Colors.CARD_BG,
            fg=Colors.PRIMARY,
            font=Fonts.SM,
            relief="groove",
            padx=8,
            pady=2,
            cursor="hand2",
            command=self._apply_inspector_names_to_grid,
        ).pack(side="left", padx=8)

        # ── 3. Scrollable Grid Container ──
        grid_container = tk.Frame(
            self,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        grid_container.pack(fill="both", expand=True, padx=12, pady=4)

        # Canvas with scrollbars
        canvas = tk.Canvas(grid_container, bg=Colors.CARD_BG, highlightthickness=0)
        v_scroll = ttk.Scrollbar(grid_container, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(grid_container, orient="horizontal", command=canvas.xview)

        self.table_frame = tk.Frame(canvas, bg=Colors.CARD_BG)
        self.table_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Pack scrollbars and canvas
        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel scroll binding on hover
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.bind("<Shift-MouseWheel>", _on_shift_mousewheel)

        self._build_grid_cells()

        # ── 4. Bottom Legend & Status Bar ──
        bottom_bar = tk.Frame(self, bg=Colors.BG)
        bottom_bar.pack(fill="x", padx=12, pady=(4, 8))

        tk.Label(
            bottom_bar,
            text="🟢 V : Normal (Bình thường - Click để đổi sang X)",
            bg=Colors.BG,
            fg=Colors.SUCCESS,
            font=Fonts.BOLD,
        ).pack(side="left", padx=8)

        tk.Label(
            bottom_bar,
            text="🔴 X : Abnormal (Bất thường - Click để đổi sang V)",
            bg=Colors.BG,
            fg=Colors.DANGER,
            font=Fonts.BOLD,
        ).pack(side="left", padx=16)

        self.lbl_status = tk.Label(
            bottom_bar,
            text="Sẵn sàng.",
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.SM,
        )
        self.lbl_status.pack(side="right", padx=12)

    def _build_grid_cells(self) -> None:
        """Draws the 28 items x 24 hourly columns grid matching Image 4."""
        tf = self.table_frame

        # ── Row 0: Shift Headers ──
        # Blank corner
        tk.Label(
            tf,
            text="",
            bg=Colors.CARD_BG,
            width=34,
            relief="ridge",
            bd=1,
        ).grid(row=0, column=0, columnspan=2, sticky="nsew")

        # 1st Shift Header
        lbl_s1 = tk.Label(
            tf,
            text="1st Shift (8:00 – 19:00)",
            bg="#FFF2CC",
            fg="#7F6000",
            font=("Segoe UI", 9, "bold"),
            relief="ridge",
            bd=1,
            pady=3,
        )
        lbl_s1.grid(row=0, column=2, columnspan=12, sticky="nsew")

        # 2nd Shift Header
        lbl_s2 = tk.Label(
            tf,
            text="2nd Shift (20:00 – 7:00)",
            bg="#FFF2CC",
            fg="#7F6000",
            font=("Segoe UI", 9, "bold"),
            relief="ridge",
            bd=1,
            pady=3,
        )
        lbl_s2.grid(row=0, column=14, columnspan=12, sticky="nsew")

        # ── Row 1: Hourly Column Headers ──
        tk.Label(
            tf,
            text="Phân nhóm",
            bg="#F2F2F2",
            font=Fonts.BOLD,
            width=12,
            relief="ridge",
            bd=1,
            pady=2,
        ).grid(row=1, column=0, sticky="nsew")

        tk.Label(
            tf,
            text="Hạng mục kiểm tra",
            bg="#F2F2F2",
            font=Fonts.BOLD,
            width=22,
            anchor="w",
            padx=6,
            relief="ridge",
            bd=1,
            pady=2,
        ).grid(row=1, column=1, sticky="nsew")

        for idx, hour in enumerate(ALL_HOURS):
            lbl_hour = tk.Label(
                tf,
                text=hour,
                bg="#FFF9E6",
                fg=Colors.TEXT_MAIN,
                font=("Segoe UI", 8, "bold"),
                width=5,
                relief="ridge",
                bd=1,
                pady=2,
            )
            lbl_hour.grid(row=1, column=2 + idx, sticky="nsew")

        # ── Rows 2 to 29: Inspection Items ──
        # Track category spans
        prev_cat = ""
        cat_start_row = 2

        for i_idx, (r_num, category, item_name, def_val) in enumerate(INSPECTION_ITEMS):
            grid_row = 2 + i_idx

            # Column 0: Category
            cat_text = category or ""
            if cat_text != prev_cat:
                prev_cat = cat_text
                # Create category label
                cat_lbl = tk.Label(
                    tf,
                    text=cat_text,
                    bg="#F8F9FA",
                    fg=Colors.TEXT_MAIN,
                    font=("Segoe UI", 9, "bold"),
                    width=12,
                    relief="ridge",
                    bd=1,
                )
                cat_lbl.grid(row=grid_row, column=0, sticky="nsew")
            else:
                # Same category continuation
                tk.Label(
                    tf,
                    text="",
                    bg="#F8F9FA",
                    width=12,
                    relief="ridge",
                    bd=1,
                ).grid(row=grid_row, column=0, sticky="nsew")

            # Column 1: Item Label
            tk.Label(
                tf,
                text=item_name,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_MAIN,
                font=("Segoe UI", 9, "bold" if not category else "normal"),
                anchor="w",
                padx=6,
                relief="ridge",
                bd=1,
            ).grid(row=grid_row, column=1, sticky="nsew")

            # Columns 2 to 25: 24 Hours
            is_entry_item = item_name in ("Temp (°C)", "Humidity(%)", "Man IN-OUT")
            for h_idx, hour in enumerate(ALL_HOURS):
                col_idx = 2 + h_idx

                if is_entry_item:
                    # Editable Entry
                    ent = tk.Entry(
                        tf,
                        width=5,
                        justify="center",
                        font=("Segoe UI", 8),
                        relief="solid",
                        bd=1,
                    )
                    ent.insert(0, def_val)
                    ent.grid(row=grid_row, column=col_idx, sticky="nsew", padx=1, pady=1)
                    self._cells[(item_name, hour)] = ent
                else:
                    # Clickable V / X label
                    lbl_val = tk.Label(
                        tf,
                        text="V",
                        bg="#E8F5E9",
                        fg=Colors.SUCCESS,
                        font=("Segoe UI", 9, "bold"),
                        width=5,
                        relief="ridge",
                        bd=1,
                        cursor="hand2",
                    )
                    lbl_val.grid(row=grid_row, column=col_idx, sticky="nsew", padx=1, pady=1)
                    lbl_val.bind("<Button-1>", lambda e, it=item_name, hr=hour: self._toggle_cell(it, hr))
                    self._cells[(item_name, hour)] = lbl_val

        # ── Row 30: Inspected by ──
        row_insp = 2 + len(INSPECTION_ITEMS)
        tk.Label(
            tf,
            text="",
            bg="#F8F9FA",
            relief="ridge",
            bd=1,
        ).grid(row=row_insp, column=0, sticky="nsew")

        tk.Label(
            tf,
            text="Inspected by",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=6,
            relief="ridge",
            bd=1,
        ).grid(row=row_insp, column=1, sticky="nsew")

        for h_idx, hour in enumerate(ALL_HOURS):
            col_idx = 2 + h_idx
            ent_insp = tk.Entry(
                tf,
                width=5,
                justify="center",
                font=("Segoe UI", 8),
                relief="solid",
                bd=1,
            )
            default_name = "Nghia" if hour in SHIFT_1_HOURS else "Huy"
            ent_insp.insert(0, default_name)
            ent_insp.grid(row=row_insp, column=col_idx, sticky="nsew", padx=1, pady=1)
            self._inspector_cells[hour] = ent_insp

        # ── Row 31: Remarks ──
        row_rem = row_insp + 1
        tk.Label(
            tf,
            text="",
            bg="#F8F9FA",
            relief="ridge",
            bd=1,
        ).grid(row=row_rem, column=0, sticky="nsew")

        tk.Label(
            tf,
            text="Remarks",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=6,
            relief="ridge",
            bd=1,
        ).grid(row=row_rem, column=1, sticky="nsew")

        self._remark_s1_entry = tk.Entry(tf, font=("Segoe UI", 9), relief="solid", bd=1)
        self._remark_s1_entry.grid(row=row_rem, column=2, columnspan=12, sticky="nsew", padx=1, pady=2)

        self._remark_s2_entry = tk.Entry(tf, font=("Segoe UI", 9), relief="solid", bd=1)
        self._remark_s2_entry.grid(row=row_rem, column=14, columnspan=12, sticky="nsew", padx=1, pady=2)

        # ── Row 32: Inspection Details ──
        row_det = row_rem + 1
        tk.Label(
            tf,
            text="",
            bg="#F8F9FA",
            relief="ridge",
            bd=1,
        ).grid(row=row_det, column=0, sticky="nsew")

        tk.Label(
            tf,
            text="Inspection Details",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=6,
            relief="ridge",
            bd=1,
        ).grid(row=row_det, column=1, sticky="nsew")

        self._details_s1_entry = tk.Entry(tf, font=("Segoe UI", 9), relief="solid", bd=1)
        self._details_s1_entry.grid(row=row_det, column=2, columnspan=12, sticky="nsew", padx=1, pady=2)

        self._details_s2_entry = tk.Entry(tf, font=("Segoe UI", 9), relief="solid", bd=1)
        self._details_s2_entry.grid(row=row_det, column=14, columnspan=12, sticky="nsew", padx=1, pady=2)

    def _toggle_cell(self, item_name: str, hour: str) -> None:
        """Toggles a cell between V (normal) and X (abnormal)."""
        widget = self._cells.get((item_name, hour))
        if not widget or not isinstance(widget, tk.Label):
            return

        curr = widget.cget("text")
        new_val = "X" if curr == "V" else "V"
        color = Colors.DANGER if new_val == "X" else Colors.SUCCESS
        bg = "#FFEEEE" if new_val == "X" else "#E8F5E9"
        widget.config(text=new_val, fg=color, bg=bg)

    def _apply_inspector_names_to_grid(self) -> None:
        """Applies inspector names from top inputs into all 24 hour cells."""
        name_s1 = self.entry_insp_s1.get().strip()
        name_s2 = self.entry_insp_s2.get().strip()

        for hour in SHIFT_1_HOURS:
            ent = self._inspector_cells.get(hour)
            if ent:
                ent.delete(0, tk.END)
                ent.insert(0, name_s1)

        for hour in SHIFT_2_HOURS:
            ent = self._inspector_cells.get(hour)
            if ent:
                ent.delete(0, tk.END)
                ent.insert(0, name_s2)

        self.lbl_status.config(text="Đã cập nhật tên người kiểm tra vào các cột giờ.")

    def fill_default_data(self) -> None:
        """Fills entire grid with Image 4 default values."""
        name_s1 = self.entry_insp_s1.get().strip() or "Nghia"
        name_s2 = self.entry_insp_s2.get().strip() or "Huy"

        # Check shift info if available
        if self.get_shift_info_cb:
            info = self.get_shift_info_cb()
            user = info.get("user", "")
            shift = info.get("shift", "Ca Ngày")
            if user:
                if "Ngày" in shift or "1" in shift:
                    name_s1 = user
                    self.entry_insp_s1.delete(0, tk.END)
                    self.entry_insp_s1.insert(0, name_s1)
                else:
                    name_s2 = user
                    self.entry_insp_s2.delete(0, tk.END)
                    self.entry_insp_s2.insert(0, name_s2)

        for _, _, item_name, def_val in INSPECTION_ITEMS:
            for hour in ALL_HOURS:
                widget = self._cells.get((item_name, hour))
                if not widget:
                    continue
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, def_val)
                elif isinstance(widget, tk.Label):
                    widget.config(text="V", fg=Colors.SUCCESS, bg="#E8F5E9")

        self._apply_inspector_names_to_grid()
        self.lbl_status.config(text="⚡ Đã tạo dữ liệu mặc định (22°C, 46%, tất cả V, '-' cho Man IN-OUT).")

    def _collect_current_data(self) -> Dict[str, Any]:
        """Extracts current visual grid and metadata into dictionary."""
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d")

        items_data: Dict[str, Dict[str, str]] = {}
        for _, _, item_name, _ in INSPECTION_ITEMS:
            items_data[item_name] = {}
            for hour in ALL_HOURS:
                w = self._cells.get((item_name, hour))
                if isinstance(w, tk.Entry):
                    items_data[item_name][hour] = w.get().strip()
                elif isinstance(w, tk.Label):
                    items_data[item_name][hour] = w.cget("text")

        inspectors_data: Dict[str, str] = {}
        for hour in ALL_HOURS:
            w_insp = self._inspector_cells.get(hour)
            inspectors_data[hour] = w_insp.get().strip() if w_insp else ""

        remarks = {
            "shift1": self._remark_s1_entry.get().strip() if self._remark_s1_entry else "",
            "shift2": self._remark_s2_entry.get().strip() if self._remark_s2_entry else "",
        }
        details = {
            "shift1": self._details_s1_entry.get().strip() if self._details_s1_entry else "",
            "shift2": self._details_s2_entry.get().strip() if self._details_s2_entry else "",
        }

        return {
            "date": date_str,
            "items": items_data,
            "inspectors": inspectors_data,
            "remarks": remarks,
            "details": details,
        }

    def load_data_for_date(self) -> None:
        """Loads data from database for the currently selected date."""
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d")
        data = load_daily_inspection(date_str)

        if not data:
            # If no data exists yet, generate defaults
            self.fill_default_data()
            self.lbl_status.config(
                text=f"ℹ️ Chưa có dữ liệu ngày {date_str}. Đã điền mẫu mặc định. Bấm 'Lưu Dữ Liệu' để ghi nhận."
            )
            return

        # Populate grid with loaded data
        items = data.get("items", {})
        for item_name, hour_dict in items.items():
            for hour, val in hour_dict.items():
                widget = self._cells.get((item_name, hour))
                if not widget:
                    continue
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, val)
                elif isinstance(widget, tk.Label):
                    color = Colors.DANGER if val == "X" else Colors.SUCCESS
                    bg = "#FFEEEE" if val == "X" else "#E8F5E9"
                    widget.config(text=val, fg=color, bg=bg)

        # Populate inspectors
        inspectors = data.get("inspectors", {})
        for hour, name in inspectors.items():
            ent = self._inspector_cells.get(hour)
            if ent:
                ent.delete(0, tk.END)
                ent.insert(0, name)

        if "8:00" in inspectors:
            self.entry_insp_s1.delete(0, tk.END)
            self.entry_insp_s1.insert(0, inspectors["8:00"])
        if "20:00" in inspectors:
            self.entry_insp_s2.delete(0, tk.END)
            self.entry_insp_s2.insert(0, inspectors["20:00"])

        # Populate remarks and details
        remarks = data.get("remarks", {})
        if self._remark_s1_entry:
            self._remark_s1_entry.delete(0, tk.END)
            self._remark_s1_entry.insert(0, remarks.get("shift1", ""))
        if self._remark_s2_entry:
            self._remark_s2_entry.delete(0, tk.END)
            self._remark_s2_entry.insert(0, remarks.get("shift2", ""))

        details = data.get("details", {})
        if self._details_s1_entry:
            self._details_s1_entry.delete(0, tk.END)
            self._details_s1_entry.insert(0, details.get("shift1", ""))
        if self._details_s2_entry:
            self._details_s2_entry.delete(0, tk.END)
            self._details_s2_entry.insert(0, details.get("shift2", ""))

        self.lbl_status.config(text=f"✅ Đã tải dữ liệu kiểm tra ngày {date_str} từ cơ sở dữ liệu.")

    def save_data(self) -> None:
        """Saves current grid data to SQLite."""
        data = self._collect_current_data()
        date_str = data["date"]

        ok, msg = save_daily_inspection(date_str, data)
        if ok:
            messagebox.showinfo("Lưu thành công", msg)
            self.lbl_status.config(text=f"✅ {msg}")
        else:
            messagebox.showerror("Lỗi lưu dữ liệu", msg)
            self.lbl_status.config(text=f"❌ {msg}")

    def export_excel(self) -> None:
        """
        Exports daily inspection to monthly master file:
        D:\\Report\\<YYYY>\\<Month>\\Daily inspection <MM-YYYY>.xlsx
        Sheet tab: DD-MM-YYYY (e.g. 29-10-2026)
        """
        data = self._collect_current_data()
        date_str = data["date"]
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            dt = datetime.now()

        default_target_path = get_daily_inspection_master_path(dt)
        sheet_name = get_daily_sheet_name(dt)

        # Prompt user: save to master file or custom file
        choice = messagebox.askyesnocancel(
            "Xuất Daily Inspection",
            f"Hệ thống sẽ xuất báo cáo vào tab:\n📑 [{sheet_name}]\n\n"
            f"Trong file Master tháng:\n📁 {default_target_path}\n\n"
            "• Chọn [Yes] để ghi trực tiếp vào file Master này.\n"
            "• Chọn [No] để chọn một file Excel khác.\n"
            "• Chọn [Cancel] để hủy thao tác.",
        )
        if choice is None:
            return

        if choice is True:
            target_file = default_target_path
        else:
            target_file = filedialog.askopenfilename(
                title="Chọn file Daily inspection để ghi thêm tab",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialdir=str(default_target_path.parent) if default_target_path.parent.exists() else None,
                initialfile=default_target_path.name,
            )
            if not target_file:
                target_file = filedialog.asksaveasfilename(
                    title="Hoặc lưu thành file mới",
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=default_target_path.name,
                )
                if not target_file:
                    return

        # Auto-save to DB first so nothing is lost
        save_daily_inspection(date_str, data)

        ok, msg = export_daily_inspection_to_excel(
            date_str=date_str,
            data=data,
            filepath=target_file,
        )

        if ok:
            if messagebox.askyesno("Xuất thành công", f"{msg}\n\nBạn có muốn mở thư mục chứa file không?"):
                try:
                    os.startfile(Path(target_file).parent)
                except Exception:
                    pass
        else:
            messagebox.showerror("Lỗi xuất file", msg)
