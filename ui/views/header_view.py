"""
HeaderView Component.

Displays the shift information bar, including Department, Date, Shift (Day/Night),
and active Operator selector.
"""
from typing import Any, Callable, Dict, Optional
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

from config.constants import Colors, Fonts, SHIFT_OPTIONS
from services.session_service import session_service


class HeaderView(tk.Frame):
    """
    Application top bar displaying shift metadata and operator selection.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_operator_changed: Optional[Callable[[str], Any]] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=Colors.CARD_BG,
            height=76,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            **kwargs,
        )
        self.on_operator_changed = on_operator_changed

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs header widgets."""
        # App branding / Title
        title_label = tk.Label(
            self,
            text="🚀 IT Shift Report",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.HEADER,
        )
        title_label.pack(side="left", padx=20, pady=12)

        # Container for Shift Info inputs
        info_panel = tk.Frame(self, bg=Colors.CARD_BG)
        info_panel.pack(side="right", padx=16, pady=10)

        # 1. Dept Field
        dept_frame = tk.Frame(info_panel, bg=Colors.CARD_BG)
        dept_frame.pack(side="left", padx=8)
        tk.Label(
            dept_frame,
            text="DEPT",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.XS,
        ).pack()
        self.dept_entry = tk.Entry(
            dept_frame,
            width=8,
            font=Fonts.BOLD,
            bg=Colors.CARD_BG,
            relief="flat",
            justify="center",
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        self.dept_entry.insert(0, "IT")
        self.dept_entry.pack(ipady=3)

        # 2. Date Field
        date_frame = tk.Frame(info_panel, bg=Colors.CARD_BG)
        date_frame.pack(side="left", padx=8)
        tk.Label(
            date_frame,
            text="DATE",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.XS,
        ).pack()
        self.date_entry = DateEntry(
            date_frame,
            width=12,
            font=Fonts.BOLD,
            date_pattern="yyyy-mm-dd",
            background=Colors.PRIMARY,
            foreground="white",
            headersbackground=Colors.PRIMARY,
            justify="center",
            borderwidth=1,
        )
        self.date_entry.pack()

        # 3. Shift Field (Ca Ngày / Ca Đêm)
        shift_frame = tk.Frame(info_panel, bg=Colors.CARD_BG)
        shift_frame.pack(side="left", padx=8)
        tk.Label(
            shift_frame,
            text="SHIFT",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.XS,
        ).pack()
        self.shift_cb = ttk.Combobox(
            shift_frame,
            values=SHIFT_OPTIONS,
            state="readonly",
            width=10,
            font=Fonts.BOLD,
            justify="center",
        )
        self.shift_cb.set(SHIFT_OPTIONS[0])
        self.shift_cb.pack()

        # 4. Operator / User Field (Combobox for flexible staff selection)
        user_frame = tk.Frame(info_panel, bg=Colors.CARD_BG)
        user_frame.pack(side="left", padx=8)
        tk.Label(
            user_frame,
            text="NGƯỜI TRỰC",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.XS,
        ).pack()

        operators = session_service.get_available_operators()
        self.user_cb = ttk.Combobox(
            user_frame,
            values=operators,
            width=18,
            font=Fonts.BOLD,
            justify="center",
        )
        current = session_service.current_operator
        self.user_cb.set(current if current in operators else (operators[0] if operators else "admin"))
        self.user_cb.pack()
        self.user_cb.bind("<<ComboboxSelected>>", self._on_user_selected)
        self.user_cb.bind("<FocusOut>", self._on_user_selected)

    def _on_user_selected(self, *_) -> None:
        """Updates active session operator when combobox changes."""
        selected_user = self.user_cb.get().strip()
        if selected_user:
            session_service.current_operator = selected_user
            if self.on_operator_changed:
                self.on_operator_changed(selected_user)

    def get_shift_info(self) -> Dict[str, str]:
        """Returns the current values of all shift header fields."""
        return {
            "dept": self.dept_entry.get().strip() or "IT",
            "date": self.date_entry.get_date().strftime("%Y-%m-%d"),
            "shift": self.shift_cb.get(),
            "user": self.user_cb.get().strip() or session_service.current_operator,
        }
