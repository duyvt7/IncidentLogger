"""
DateTimePicker Component.

A reusable widget combining a calendar date selector and hour:minute dropdowns.
"""
from typing import Optional, Union
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

from config.constants import Colors, Fonts


class DateTimePicker(tk.Frame):
    """
    Combined DateEntry and HH:MM combobox picker.
    
    Usage:
        picker = DateTimePicker(parent)
        picker.pack()
        current_val = picker.get_formatted() # "2026-11-01 14:30"
    """

    def __init__(
        self,
        parent: tk.Widget,
        default_dt: Optional[Union[datetime, str]] = None,
        bg: str = Colors.BG,
        **kwargs,
    ):
        super().__init__(parent, bg=bg, **kwargs)

        # 1. Date Selector
        self.date_entry = DateEntry(
            self,
            width=12,
            font=Fonts.MAIN,
            date_pattern="yyyy-mm-dd",
            background=Colors.PRIMARY,
            foreground="white",
            headersbackground=Colors.PRIMARY,
            borderwidth=1,
        )
        self.date_entry.pack(side="left", padx=(0, 6))

        # 2. Hour Combobox
        hour_values = [f"{i:02d}" for i in range(24)]
        self.hour_cb = ttk.Combobox(
            self,
            values=hour_values,
            width=3,
            state="readonly",
            font=Fonts.MAIN,
            justify="center",
        )
        self.hour_cb.pack(side="left")

        # Separator ":"
        tk.Label(
            self,
            text=":",
            bg=bg,
            fg=Colors.TEXT_MAIN,
            font=Fonts.BOLD,
        ).pack(side="left", padx=2)

        # 3. Minute Combobox
        minute_values = [f"{i:02d}" for i in range(60)]
        self.min_cb = ttk.Combobox(
            self,
            values=minute_values,
            width=3,
            state="readonly",
            font=Fonts.MAIN,
            justify="center",
        )
        self.min_cb.pack(side="left")

        # Set default values
        now = datetime.now()
        if default_dt:
            self.set_datetime(default_dt)
        else:
            self.hour_cb.set(f"{now.hour:02d}")
            self.min_cb.set(f"{now.minute:02d}")

    def get_formatted(self) -> str:
        """Returns string in standard format: 'YYYY-MM-DD HH:MM'."""
        d_str = self.date_entry.get_date().strftime("%Y-%m-%d")
        h_str = self.hour_cb.get().zfill(2)
        m_str = self.min_cb.get().zfill(2)
        return f"{d_str} {h_str}:{m_str}"

    def get_date(self) -> date:
        """Returns the selected date object."""
        return self.date_entry.get_date()

    def set_datetime(self, val: Union[datetime, str]) -> None:
        """
        Sets the widget values from a datetime object or formatted string 'YYYY-MM-DD HH:MM'.
        """
        if isinstance(val, str):
            try:
                dt = datetime.strptime(val[:16], "%Y-%m-%d %H:%M")
            except Exception:
                try:
                    dt = datetime.strptime(val[:10], "%Y-%m-%d")
                except Exception:
                    dt = datetime.now()
        elif isinstance(val, datetime):
            dt = val
        else:
            dt = datetime.now()

        self.date_entry.set_date(dt.date())
        self.hour_cb.set(f"{dt.hour:02d}")
        self.min_cb.set(f"{dt.minute:02d}")
