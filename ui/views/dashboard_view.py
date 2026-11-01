"""
DashboardView Component.

Visualizes operational statistics, open incident counts, and category breakdowns.
"""
import tkinter as tk
from typing import Optional

from config.constants import Colors, Fonts
from services.incident_service import get_incident_statistics
from ui.components.stat_card import StatCard


class DashboardView(tk.Frame):
    """
    Dashboard tab showing KPI metric cards and category distribution.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, bg=Colors.BG, padx=20, pady=20, **kwargs)

        self._build_ui()
        self.refresh_statistics()

    def _build_ui(self) -> None:
        """Constructs dashboard cards and breakdown widgets."""
        # Header Label
        header_frame = tk.Frame(self, bg=Colors.BG)
        header_frame.pack(fill="x", pady=(0, 16))

        tk.Label(
            header_frame,
            text="📊 Thống kê Hoạt động IT",
            bg=Colors.BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.TITLE,
        ).pack(side="left")

        tk.Button(
            header_frame,
            text="🔄 Làm mới",
            bg=Colors.BORDER,
            fg=Colors.TEXT_DIM,
            font=Fonts.SM,
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.refresh_statistics,
        ).pack(side="right")

        # 3 KPI Stat Cards
        cards_frame = tk.Frame(self, bg=Colors.BG)
        cards_frame.pack(fill="x", pady=(0, 20))

        self.card_total = StatCard(
            cards_frame,
            title="Tổng số Sự cố",
            value="0",
            color=Colors.PRIMARY,
            icon="📌",
        )
        self.card_total.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.card_today = StatCard(
            cards_frame,
            title="Sự cố Hôm nay",
            value="0",
            color=Colors.SUCCESS,
            icon="📅",
        )
        self.card_today.pack(side="left", fill="both", expand=True, padx=4)

        self.card_open = StatCard(
            cards_frame,
            title="Đang Xử lý / Cần theo dõi",
            value="0",
            color=Colors.WARNING,
            icon="⚠️",
        )
        self.card_open.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # Category Breakdown Container
        cat_card = tk.Frame(
            self,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            padx=20,
            pady=16,
        )
        cat_card.pack(fill="both", expand=True)

        tk.Label(
            cat_card,
            text="Phân bố sự cố theo Danh mục (Category):",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.BOLD,
        ).pack(anchor="w", pady=(0, 12))

        self.cat_list_frame = tk.Frame(cat_card, bg=Colors.CARD_BG)
        self.cat_list_frame.pack(fill="both", expand=True)

    def refresh_statistics(self) -> None:
        """Fetches the latest metrics from database and updates all cards."""
        try:
            stats = get_incident_statistics()
            self.card_total.set_value(str(stats["total"]))
            self.card_today.set_value(str(stats["today"]))
            self.card_open.set_value(str(stats["open_issues"]))

            # Clear old category rows
            for child in self.cat_list_frame.winfo_children():
                child.destroy()

            by_cat = stats.get("by_category", {})
            if not by_cat:
                tk.Label(
                    self.cat_list_frame,
                    text="Chưa có dữ liệu sự cố nào.",
                    bg=Colors.CARD_BG,
                    fg=Colors.TEXT_DIM,
                    font=Fonts.MAIN,
                ).pack(anchor="w", pady=8)
                return

            for cat_name, count in by_cat.items():
                row = tk.Frame(self.cat_list_frame, bg=Colors.CARD_BG)
                row.pack(fill="x", pady=4)

                tk.Label(
                    row,
                    text=f"• {cat_name}",
                    bg=Colors.CARD_BG,
                    fg=Colors.TEXT_MAIN,
                    font=Fonts.MAIN,
                    width=28,
                    anchor="w",
                ).pack(side="left")

                tk.Label(
                    row,
                    text=f"{count} sự cố",
                    bg=Colors.SELECT_BG,
                    fg=Colors.PRIMARY,
                    font=Fonts.BOLD,
                    padx=10,
                    pady=2,
                ).pack(side="left")

        except Exception as exc:
            tk.Label(
                self.cat_list_frame,
                text=f"Không thể tải thống kê: {exc}",
                bg=Colors.CARD_BG,
                fg=Colors.DANGER,
                font=Fonts.SM,
            ).pack(anchor="w")

