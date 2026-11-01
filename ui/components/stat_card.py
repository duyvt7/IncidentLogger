"""
StatCard Component.

A reusable KPI card widget for the dashboard displaying a title and prominent metric value.
"""
import tkinter as tk
from typing import Optional

from config.constants import Colors, Fonts


class StatCard(tk.Frame):
    """
    A stylized metric/card widget with title, colored value, and subtle border.
    
    Usage:
        card = StatCard(parent, title="Total Incidents", value="53", color=Colors.PRIMARY)
        card.pack(side="left", fill="both", expand=True, padx=8)
        card.set_value("54")
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        value: str = "0",
        color: str = Colors.PRIMARY,
        icon: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=Colors.CARD_BG,
            padx=20,
            pady=18,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            **kwargs,
        )

        display_title = f"{icon} {title}" if icon else title
        self._title_label = tk.Label(
            self,
            text=display_title,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
        )
        self._title_label.pack(anchor="center")

        self._value_label = tk.Label(
            self,
            text=str(value),
            bg=Colors.CARD_BG,
            fg=color,
            font=Fonts.HEADER,
        )
        self._value_label.pack(anchor="center", pady=(4, 0))

    def set_value(self, value: str) -> None:
        """Updates the metric value displayed on the card."""
        self._value_label.configure(text=str(value))

    def set_color(self, color: str) -> None:
        """Updates the accent text color of the value."""
        self._value_label.configure(fg=color)

