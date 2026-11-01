"""
DataTable Component.

A reusable Treeview wrapper with automatic vertical and horizontal scrollbars,
column configuration, and selection helpers.
"""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import tkinter as tk
from tkinter import ttk

from config.constants import Colors, Fonts


class DataTable(tk.Frame):
    """
    Modular data table widget built on ttk.Treeview.
    
    Usage:
        columns = [
            ("id", "ID", 50),
            ("category", "Category", 140),
            ("failure", "Failure", 200),
        ]
        table = DataTable(parent, columns=columns)
        table.pack(fill="both", expand=True)
        table.insert_row(("1", "H/W", "Disk Full"), item_id="1")
    """

    def __init__(
        self,
        parent: tk.Widget,
        columns: List[Tuple[str, str, int]],
        selectmode: str = "browse",
        on_double_click: Optional[Callable[[tk.Event], Any]] = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=Colors.CARD_BG,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            **kwargs,
        )

        col_ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            selectmode=selectmode,
        )

        # Configure columns and headings
        for col_id, heading_text, width in columns:
            self.tree.heading(col_id, text=heading_text)
            anchor = "center" if width < 140 else "w"
            self.tree.column(
                col_id,
                width=width,
                minwidth=30,
                anchor=anchor,
            )

        # Scrollbars
        self.vsb = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            style="Vertical.TScrollbar",
        )
        self.hsb = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview,
            style="Horizontal.TScrollbar",
        )
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Layout in grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        if on_double_click:
            self.tree.bind("<Double-1>", on_double_click)

    def insert_row(
        self,
        values: Union[List[Any], Tuple[Any, ...]],
        item_id: Optional[str] = None,
        tags: Tuple[str, ...] = (),
    ) -> str:
        """Inserts a row into the table."""
        kwargs: Dict[str, Any] = {"values": values, "tags": tags}
        if item_id:
            kwargs["iid"] = str(item_id)
        return self.tree.insert("", "end", **kwargs)

    def clear(self) -> None:
        """Removes all rows from the table."""
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)

    def get_selected_id(self) -> Optional[int]:
        """Returns the ID (iid converted to int) of the selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        try:
            return int(selection[0])
        except (ValueError, TypeError):
            return None

    def get_selected_iid(self) -> Optional[str]:
        """Returns the raw iid string of the selected row, or None."""
        selection = self.tree.selection()
        return selection[0] if selection else None

    def get_selected_values(self) -> Optional[Tuple[Any, ...]]:
        """Returns the tuple of values for the selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return tuple(item.get("values", []))

    def bind_double_click(self, callback: Callable[[tk.Event], Any]) -> None:
        """Binds a double-click event listener to the tree."""
        self.tree.bind("<Double-1>", callback)

    def get_row_count(self) -> int:
        """Returns current row count."""
        return len(self.tree.get_children())
