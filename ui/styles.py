"""
UI Styling and ttk Theme Setup.

Applies a clean, modern flat theme across all ttk widgets (Notebook, Treeview, Combobox).
"""
import tkinter as tk
from tkinter import ttk

from config.constants import Colors, Fonts


def apply_app_styles(root: tk.Tk) -> ttk.Style:
    """
    Applies unified color palette and typography styles to ttk widgets.
    
    Args:
        root: The root Tk window.
        
    Returns:
        The configured ttk.Style instance.
    """
    style = ttk.Style(root)
    style.theme_use("clam")

    # 1. Notebook Tabs
    style.configure(
        "TNotebook",
        background=Colors.BG,
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=Colors.BORDER,
        foreground=Colors.TEXT_DIM,
        padding=(20, 8),
        font=Fonts.BOLD,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", Colors.PRIMARY)],
        foreground=[("selected", "white")],
    )

    # 2. Treeview Tables
    style.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground=Colors.TEXT_MAIN,
        rowheight=32,
        borderwidth=0,
        font=Fonts.MAIN,
    )
    style.configure(
        "Treeview.Heading",
        background=Colors.HDR_BG,
        foreground=Colors.TEXT_MAIN,
        font=Fonts.BOLD,
        relief="flat",
        borderwidth=1,
    )
    style.map(
        "Treeview",
        background=[("selected", Colors.SELECT_BG)],
        foreground=[("selected", Colors.TEXT_MAIN)],
    )

    # 3. Scrollbars
    style.configure(
        "Vertical.TScrollbar",
        background=Colors.BG,
        troughcolor="white",
        borderwidth=0,
        arrowsize=12,
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=Colors.BG,
        troughcolor="white",
        borderwidth=0,
        arrowsize=12,
    )

    # 4. Combobox
    style.configure(
        "TCombobox",
        fieldbackground="white",
        background=Colors.BG,
        foreground=Colors.TEXT_MAIN,
        font=Fonts.MAIN,
    )

    return style
