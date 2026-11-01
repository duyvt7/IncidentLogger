"""
Incident Form Dialog Component.

A modal Toplevel dialog for creating and editing IT incidents.
Uses DateTimePicker and dynamic sub-category cascading.
"""
from typing import Any, Callable, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox

from config.constants import (
    Colors,
    Fonts,
    DETAIL_STRUCTURE,
    CURRENT_SITUATION_OPTIONS,
)
from services.incident_service import (
    add_incident,
    get_incident_by_id,
    update_incident,
)
from services.session_service import session_service
from ui.components.date_time_picker import DateTimePicker


class IncidentDialog(tk.Toplevel):
    """
    Modal dialog window to create a new incident or edit an existing one.
    """

    def __init__(
        self,
        parent: tk.Widget,
        edit_id: Optional[int] = None,
        on_save: Optional[Callable[[], Any]] = None,
        default_reporter: Optional[str] = None,
        default_shift: Optional[str] = None,
    ):
        super().__init__(parent)
        self.edit_id = edit_id
        self.on_save = on_save
        self.default_reporter = default_reporter or session_service.current_operator
        self.default_shift = default_shift or "Ca Ngày"

        # Window configuration
        self.title(f"Sửa sự cố #{edit_id}" if edit_id else "Thêm sự cố mới")
        self.configure(bg=Colors.BG)
        self.geometry("600x640")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        if edit_id:
            self._load_incident_data(edit_id)

    def _build_ui(self) -> None:
        """Constructs form layout."""
        # Header Title
        title_text = f"✏️ Sửa sự cố #{self.edit_id}" if self.edit_id else "➕ Thêm sự cố mới"
        tk.Label(
            self,
            text=title_text,
            bg=Colors.BG,
            fg=Colors.PRIMARY,
            font=Fonts.TITLE,
        ).pack(pady=(16, 12))

        # Form Container
        form_frame = tk.Frame(self, bg=Colors.BG)
        form_frame.pack(fill="both", expand=True, padx=28)
        form_frame.columnconfigure(1, weight=1)

        self.fields: Dict[str, Any] = {}
        cats = [c for c, _ in DETAIL_STRUCTURE]

        # 1. Category
        self._add_row(form_frame, 0, "Category *", "category", "combo", cats)
        self.fields["category"].bind("<<ComboboxSelected>>", self._on_category_changed)

        # 2. Sub-Category
        self._add_row(form_frame, 1, "Sub-Item", "sub_category", "combo", [])

        # 3. Time (DateTimePicker)
        tk.Label(
            form_frame,
            text="Time *",
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.SM,
            anchor="e",
            width=18,
        ).grid(row=2, column=0, sticky="ne", pady=6, padx=(0, 10))

        self.time_picker = DateTimePicker(form_frame, bg=Colors.BG)
        self.time_picker.grid(row=2, column=1, sticky="w", pady=4)

        # 4. Failure (Required)
        self._add_row(form_frame, 3, "Failure *", "failure", "entry")

        # 5. Reason
        self._add_row(form_frame, 4, "Reason", "reason", "entry")

        # 6. Solution
        self._add_row(form_frame, 5, "Solution", "solution", "text")

        # 7. Current Situation
        self._add_row(
            form_frame,
            6,
            "Current Situation",
            "current_situation",
            "combo",
            CURRENT_SITUATION_OPTIONS,
        )

        # 8. Contact Number
        self._add_row(form_frame, 7, "Contact Number", "contact", "entry")

        # Trigger sub-category population for the initial category
        self._on_category_changed()

        # Action Buttons
        btn_frame = tk.Frame(self, bg=Colors.BG, pady=16)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text="💾 Lưu sự cố",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._save,
        ).pack(side="right", padx=(8, 28))

        tk.Button(
            btn_frame,
            text="Hủy bỏ",
            bg=Colors.BORDER,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.destroy,
        ).pack(side="right")

    def _add_row(
        self,
        parent: tk.Widget,
        row: int,
        label: str,
        key: str,
        widget_type: str = "entry",
        values: Optional[list] = None,
    ) -> None:
        """Helper to create a standard labeled form field."""
        tk.Label(
            parent,
            text=label,
            bg=Colors.BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.SM,
            anchor="e",
            width=18,
        ).grid(row=row, column=0, sticky="ne", pady=6, padx=(0, 10))

        if widget_type == "combo":
            widget = ttk.Combobox(
                parent,
                values=values or [],
                state="readonly",
                font=Fonts.MAIN,
            )
            if values:
                widget.set(values[0])
            widget.grid(row=row, column=1, sticky="ew", pady=4)
        elif widget_type == "text":
            widget = tk.Text(
                parent,
                height=3,
                wrap="word",
                font=Fonts.MAIN,
                relief="flat",
                highlightthickness=1,
                highlightbackground=Colors.BORDER,
            )
            widget.grid(row=row, column=1, sticky="ew", pady=4)
        else:
            widget = tk.Entry(
                parent,
                font=Fonts.MAIN,
                relief="flat",
                highlightthickness=1,
                highlightbackground=Colors.BORDER,
            )
            widget.grid(row=row, column=1, sticky="ew", ipady=4, pady=4)

        self.fields[key] = widget

    def _on_category_changed(self, *_) -> None:
        """Updates the sub-category combobox when the selected category changes."""
        selected_cat = self.fields["category"].get()
        subs = []
        for cat_name, sub_list in DETAIL_STRUCTURE:
            if cat_name == selected_cat:
                subs = sub_list
                break

        sub_cb = self.fields["sub_category"]
        if subs:
            sub_cb.configure(values=subs, state="readonly")
            sub_cb.set(subs[0])
        else:
            sub_cb.configure(values=[], state="disabled")
            sub_cb.set("")

    def _load_incident_data(self, incident_id: int) -> None:
        """Loads existing incident data into form controls."""
        row = get_incident_by_id(incident_id)
        if not row:
            messagebox.showerror("Lỗi", f"Không tìm thấy sự cố #{incident_id}", parent=self)
            self.destroy()
            return

        # Category
        self.fields["category"].set(row["category"])
        self._on_category_changed()
        if row["sub_category"]:
            self.fields["sub_category"].set(row["sub_category"])

        # Time
        if row["time"]:
            self.time_picker.set_datetime(row["time"])

        # Failure, Reason, Contact
        self.fields["failure"].delete(0, "end")
        self.fields["failure"].insert(0, row["failure"] or "")

        self.fields["reason"].delete(0, "end")
        self.fields["reason"].insert(0, row["reason"] or "")

        # Solution
        self.fields["solution"].delete("1.0", "end")
        self.fields["solution"].insert("1.0", row["solution"] or "")

        # Current Situation
        self.fields["current_situation"].set(row["current_situation"] or "Running normal")

        # Contact
        self.fields["contact"].delete(0, "end")
        self.fields["contact"].insert(0, row["contact"] or "")

    def _save(self) -> None:
        """Validates form fields and saves to database."""
        failure = self.fields["failure"].get().strip()
        if not failure:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mô tả lỗi (Failure).", parent=self)
            self.fields["failure"].focus_set()
            return

        time_val = self.time_picker.get_formatted()
        solution = self.fields["solution"].get("1.0", "end").strip()

        data = {
            "time": time_val,
            "category": self.fields["category"].get(),
            "sub_category": self.fields["sub_category"].get() or None,
            "failure": failure,
            "reason": self.fields["reason"].get().strip() or None,
            "solution": solution or None,
            "current_situation": self.fields["current_situation"].get().strip() or "Running normal",
            "contact": self.fields["contact"].get().strip() or None,
            "reporter": self.default_reporter,
            "shift": self.default_shift,
        }

        try:
            if self.edit_id:
                update_incident(self.edit_id, data)
            else:
                add_incident(data)

            if self.on_save:
                self.on_save()

            self.destroy()
        except Exception as exc:
            messagebox.showerror("Lỗi lưu sự cố", f"Không thể lưu sự cố: {exc}", parent=self)
