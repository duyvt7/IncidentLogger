"""
DetailView Component.

Manages the incident table, date filtering, search, add/edit/delete operations,
and Excel report exporting.
"""
from typing import Any, Callable, Dict, Optional, Sequence
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry

from config.constants import Colors, Fonts
from config.settings import get_db_path
from services.incident_service import (
    get_incidents,
    delete_incident,
)
from services.export_service import (
    export_shift_report_to_excel,
    get_shift_report_master_path,
    get_sheet_tab_name,
)
from ui.components.data_table import DataTable
from ui.dialogs.incident_dialog import IncidentDialog


class DetailView(tk.Frame):
    """
    Incident list table view with search, filter, CRUD dialogs, and Excel export.
    """

    def __init__(
        self,
        parent: tk.Widget,
        get_shift_info_cb: Optional[Callable[[], Dict[str, str]]] = None,
        get_hmi_data_cb: Optional[Callable[[], Dict[str, Any]]] = None,
        on_data_changed_cb: Optional[Callable[[], Any]] = None,
        **kwargs,
    ):
        super().__init__(parent, bg=Colors.BG, **kwargs)
        self.get_shift_info_cb = get_shift_info_cb
        self.get_hmi_data_cb = get_hmi_data_cb
        self.on_data_changed_cb = on_data_changed_cb

        self.filter_active: bool = False

        self._build_ui()
        self.load_today_incidents()

    def _build_ui(self) -> None:
        """Constructs action bar, filter bar, table, and status bar."""
        # 1. Top Action Bar
        action_bar = tk.Frame(
            self,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        action_bar.pack(fill="x", padx=12, pady=(10, 6))

        tk.Label(
            action_bar,
            text="📝 Danh sách Sự cố (Detail)",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.TITLE,
        ).pack(side="left", padx=16, pady=10)

        # Buttons on right
        tk.Button(
            action_bar,
            text="📤 Xuất Báo Cáo Excel",
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
            text="➕ Thêm sự cố",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.open_add_dialog,
        ).pack(side="right", padx=4, pady=8)

        # 2. Filter Bar
        filter_bar = tk.Frame(self, bg=Colors.BG)
        filter_bar.pack(fill="x", padx=12, pady=4)

        tk.Label(
            filter_bar,
            text="📅 Từ ngày:",
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
        ).pack(side="left", padx=(0, 4))

        self.date_from = DateEntry(
            filter_bar,
            width=12,
            font=Fonts.MAIN,
            date_pattern="yyyy-mm-dd",
            background=Colors.PRIMARY,
            foreground="white",
            headersbackground=Colors.PRIMARY,
        )
        self.date_from.pack(side="left", padx=(0, 8))

        tk.Label(
            filter_bar,
            text="đến ngày:",
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
        ).pack(side="left", padx=(0, 4))

        self.date_to = DateEntry(
            filter_bar,
            width=12,
            font=Fonts.MAIN,
            date_pattern="yyyy-mm-dd",
            background=Colors.PRIMARY,
            foreground="white",
            headersbackground=Colors.PRIMARY,
        )
        self.date_to.pack(side="left", padx=(0, 8))

        tk.Button(
            filter_bar,
            text="🔍 Lọc",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=14,
            pady=3,
            cursor="hand2",
            command=self.filter_by_date_range,
        ).pack(side="left", padx=4)

        tk.Button(
            filter_bar,
            text="📅 Hôm nay",
            bg=Colors.BORDER,
            fg=Colors.TEXT_MAIN,
            font=Fonts.MAIN,
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.load_today_incidents,
        ).pack(side="left", padx=4)

        tk.Button(
            filter_bar,
            text="↺ Xem tất cả",
            bg=Colors.BORDER,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.load_all_incidents,
        ).pack(side="left", padx=4)

        # 3. Main Incident Table
        columns = [
            ("stt", "STT", 45),
            ("category", "Category", 130),
            ("sub_item", "Sub-Item", 160),
            ("time", "Time", 115),
            ("failure", "Failure", 170),
            ("reason", "Reason", 115),
            ("solution", "Solution", 180),
            ("situation", "Current Situation", 140),
            ("contact", "Contact Number", 110),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_double_click=lambda e: self.edit_selected(),
        )
        self.table.pack(fill="both", expand=True, padx=12, pady=4)

        # 4. Bottom Status & Action Bar
        status_bar = tk.Frame(
            self,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        status_bar.pack(fill="x", padx=12, pady=(2, 10))

        self.lbl_status = tk.Label(
            status_bar,
            text="",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
        )
        self.lbl_status.pack(side="left", padx=16, pady=8)

        tk.Button(
            status_bar,
            text="🗑️ Xóa",
            bg=Colors.DANGER,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.delete_selected,
        ).pack(side="right", padx=(4, 16), pady=6)

        tk.Button(
            status_bar,
            text="✏️ Sửa",
            bg=Colors.WARNING,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.edit_selected,
        ).pack(side="right", padx=4, pady=6)

    def _populate_table(self, rows: Sequence[Any]) -> None:
        """Helper to clear and populate table with incident rows."""
        self.table.clear()
        for i, r in enumerate(rows, 1):
            self.table.insert_row(
                (
                    i,
                    r["category"],
                    r["sub_category"] or "",
                    r["time"],
                    r["failure"],
                    r["reason"] or "",
                    r["solution"] or "",
                    r["current_situation"] or "",
                    r["contact"] or "",
                ),
                item_id=str(r["id"]),
            )

    def load_today_incidents(self) -> None:
        """Loads incidents for today only (default view)."""
        self.filter_active = False
        today_str = datetime.now().strftime("%Y-%m-%d")
        try:
            self.date_from.set_date(datetime.now().date())
            self.date_to.set_date(datetime.now().date())
        except Exception:
            pass

        try:
            rows = get_incidents(start_date=today_str, end_date=today_str)
            self._populate_table(rows)
            db_name = get_db_path().name
            self.lbl_status.configure(
                text=f"📅 Hôm nay: {today_str} — 📂 {db_name} — Số lượng: {len(rows)} sự cố"
            )
        except Exception as exc:
            messagebox.showerror("Lỗi tải dữ liệu", f"Không thể tải danh sách sự cố hôm nay: {exc}")

    def load_all_incidents(self) -> None:
        """Loads all historical incidents without date filtering."""
        self.filter_active = False
        try:
            rows = get_incidents()
            self._populate_table(rows)
            db_name = get_db_path().name
            self.lbl_status.configure(
                text=f"📂 Cơ sở dữ liệu: {db_name} | Tất cả: {len(rows)} sự cố"
            )
        except Exception as exc:
            messagebox.showerror("Lỗi tải dữ liệu", f"Không thể tải danh sách sự cố: {exc}")

    def filter_by_date_range(self) -> None:
        """Filters table records by selected date range."""
        self.filter_active = True
        d1 = self.date_from.get_date().strftime("%Y-%m-%d")
        d2 = self.date_to.get_date().strftime("%Y-%m-%d")

        try:
            rows = get_incidents(start_date=d1, end_date=d2)
            self._populate_table(rows)
            db_name = get_db_path().name
            self.lbl_status.configure(
                text=f"📅 Lọc: {d1} ➔ {d2} — 📂 {db_name} — Kết quả: {len(rows)} sự cố"
            )
        except Exception as exc:
            messagebox.showerror("Lỗi lọc dữ liệu", f"Lỗi khi lọc: {exc}")

    def open_add_dialog(self) -> None:
        """Opens incident dialog to add a new record."""
        shift_info = self.get_shift_info_cb() if self.get_shift_info_cb else {}
        IncidentDialog(
            self,
            edit_id=None,
            on_save=self._on_incident_saved,
            default_reporter=shift_info.get("user"),
            default_shift=shift_info.get("shift"),
        )

    def edit_selected(self) -> None:
        """Opens incident dialog for the selected row."""
        sel_id = self.table.get_selected_id()
        if not sel_id:
            messagebox.showwarning("Chưa chọn bản ghi", "Vui lòng chọn một sự cố trong bảng để sửa.")
            return

        shift_info = self.get_shift_info_cb() if self.get_shift_info_cb else {}
        IncidentDialog(
            self,
            edit_id=sel_id,
            on_save=self._on_incident_saved,
            default_reporter=shift_info.get("user"),
            default_shift=shift_info.get("shift"),
        )

    def delete_selected(self) -> None:
        """Deletes the selected incident record after user confirmation."""
        sel_id = self.table.get_selected_id()
        if not sel_id:
            messagebox.showwarning("Chưa chọn bản ghi", "Vui lòng chọn một sự cố trong bảng để xóa.")
            return

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa sự cố #{sel_id}?"):
            try:
                delete_incident(sel_id)
                self._on_incident_saved()
            except Exception as exc:
                messagebox.showerror("Lỗi xóa sự cố", f"Không thể xóa sự cố: {exc}")

    def _on_incident_saved(self) -> None:
        """Reloads table and triggers parent data change callback."""
        if self.filter_active:
            self.filter_by_date_range()
        else:
            self.load_today_incidents()

        if self.on_data_changed_cb:
            self.on_data_changed_cb()

    def export_excel(self) -> None:
        """Prompts destination or auto-exports into monthly master workbook tab."""
        import os
        from pathlib import Path

        shift_info = self.get_shift_info_cb() if self.get_shift_info_cb else {}
        date_str = shift_info.get("date", datetime.now().strftime("%Y-%m-%d"))
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            dt = datetime.now()

        sel_shift = shift_info.get("shift", "Ca Ngày")
        default_target_path = get_shift_report_master_path(dt)
        sheet_name = get_sheet_tab_name(dt, sel_shift)

        # Ask user: export directly to master file, choose another file, or cancel
        choice = messagebox.askyesnocancel(
            "Xuất Shift Report",
            f"Hệ thống sẽ xuất báo cáo vào tab:\n📑 [{sheet_name}]\n\n"
            f"Trong file Master tháng:\n📁 {default_target_path}\n\n"
            "• Chọn [Yes] để ghi trực tiếp vào file Master này.\n"
            "• Chọn [No] để chọn một file Excel khác.\n"
            "• Chọn [Cancel] để hủy thao tác.",
        )
        if choice is None:
            return  # User clicked Cancel

        if choice is True:
            target_file = default_target_path
        else:
            target_file = filedialog.askopenfilename(
                title="Chọn file Shift Report để ghi thêm tab",
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

        # Fetch incidents
        if self.filter_active:
            d1 = self.date_from.get_date().strftime("%Y-%m-%d")
            d2 = self.date_to.get_date().strftime("%Y-%m-%d")
            rows = get_incidents(start_date=d1, end_date=d2)
        else:
            # Default to incidents of this shift's date
            rows = get_incidents(start_date=date_str, end_date=date_str)

        incidents = [dict(r) for r in rows]
        hmi_data = self.get_hmi_data_cb() if self.get_hmi_data_cb else {}

        ok, msg = export_shift_report_to_excel(
            filepath=target_file,
            dept=shift_info.get("dept", "IT"),
            section="Dx Engineering Team",
            prepared_by=shift_info.get("user", ""),
            group="B",
            shift=sel_shift,
            date_val=dt,
            incidents=incidents,
            hmi_data=hmi_data,
        )

        if ok:
            if messagebox.askyesno("Xuất thành công", f"{msg}\n\nBạn có muốn mở thư mục chứa file không?"):
                try:
                    os.startfile(Path(target_file).parent)
                except Exception:
                    pass
        else:
            messagebox.showerror("Lỗi xuất file", msg)

