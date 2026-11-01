"""
HMIView Component.

Interactive health-check monitoring table for industrial manufacturing lines
(MES Link SCC, SCC Link PLC, Application Link, and Remarks).
"""
from typing import Any, Dict
import logging
import tkinter as tk
from tkinter import ttk, messagebox

from config.constants import Colors, Fonts, HMI_LINES, HMI_COLS, HMI_STATUS_OPTIONS
from services.hmi_service import save_hmi_status, load_hmi_status

logger = logging.getLogger(__name__)


class HmiView(tk.Frame):
    """
    HMI Checking tab with editable line health check table and persistence.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, bg=Colors.BG, padx=20, pady=20, **kwargs)

        self._entries: Dict[str, Dict[str, Any]] = {}
        self._build_ui()
        self.load_saved_status()

    def _build_ui(self) -> None:
        """Constructs HMI table card and grid."""
        card = tk.Frame(
            self,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            padx=24,
            pady=20,
        )
        card.pack(fill="both", expand=True)

        # Header Title
        tk.Label(
            card,
            text="✅ 3. HMI Checking",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_MAIN,
            font=Fonts.TITLE,
        ).pack(anchor="w", pady=(0, 16))

        # Grid Container
        grid_frame = tk.Frame(card, bg=Colors.CARD_BG)
        grid_frame.pack(fill="x")

        # Table Column Headers
        all_headers = ["Chuyền / Line"] + HMI_COLS
        for col_idx, header_text in enumerate(all_headers):
            lbl = tk.Label(
                grid_frame,
                text=header_text,
                bg=Colors.HDR_BG,
                fg=Colors.TEXT_MAIN,
                font=Fonts.BOLD,
                width=18,
                relief="flat",
                highlightthickness=1,
                highlightbackground=Colors.BORDER,
            )
            lbl.grid(row=0, column=col_idx, padx=2, pady=2, sticky="ew")

        # Line Rows
        for row_idx, line in enumerate(HMI_LINES, 1):
            tk.Label(
                grid_frame,
                text=line,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_MAIN,
                font=Fonts.BOLD,
                width=18,
                anchor="w",
                padx=8,
            ).grid(row=row_idx, column=0, padx=2, pady=4)

            self._entries[line] = {}
            for col_idx, col_name in enumerate(HMI_COLS, 1):
                if col_name == "Remark":
                    widget = tk.Entry(
                        grid_frame,
                        font=Fonts.MAIN,
                        relief="flat",
                        highlightthickness=1,
                        highlightbackground=Colors.BORDER,
                    )
                else:
                    widget = ttk.Combobox(
                        grid_frame,
                        values=HMI_STATUS_OPTIONS,
                        width=14,
                        state="readonly",
                        font=Fonts.MAIN,
                        justify="center",
                    )
                    widget.set("OK")

                widget.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="ew")
                self._entries[line][col_name] = widget

        # Save Button
        save_btn = tk.Button(
            card,
            text="💾 Lưu trạng thái HMI",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.save_status,
        )
        save_btn.pack(anchor="e", pady=(20, 0))

    def get_hmi_data(self) -> Dict[str, Dict[str, str]]:
        """Collects the current values from the grid."""
        data: Dict[str, Dict[str, str]] = {}
        for line in HMI_LINES:
            data[line] = {}
            for col_name in HMI_COLS:
                widget = self._entries[line][col_name]
                data[line][col_name] = widget.get().strip()
        return data

    def save_status(self) -> None:
        """Saves current HMI data to database."""
        try:
            data = self.get_hmi_data()
            save_hmi_status(data)
            messagebox.showinfo("Thành công", "Đã lưu trạng thái HMI vào cơ sở dữ liệu!")
        except Exception as exc:
            messagebox.showerror("Lỗi lưu HMI", f"Không thể lưu trạng thái HMI: {exc}")

    def load_saved_status(self) -> None:
        """Loads saved HMI data from database into grid."""
        try:
            saved_data = load_hmi_status()
            for line, cols in saved_data.items():
                if line in self._entries:
                    for col_name, val in cols.items():
                        if col_name in self._entries[line]:
                            widget = self._entries[line][col_name]
                            if isinstance(widget, ttk.Combobox):
                                widget.set(val or "OK")
                            else:
                                widget.delete(0, "end")
                                widget.insert(0, val or "")
        except Exception as exc:
            logger.error("Lỗi tải HMI: %s", exc)

