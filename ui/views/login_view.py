"""
LoginView Component (Extensible Auth Module).

A standalone login screen component ready for when authentication is enabled
in the future via `config.settings.AppSettings.auth_enabled = True`.
"""
from typing import Any, Callable, Optional
import tkinter as tk
from tkinter import ttk, messagebox

from config.constants import Colors, Fonts
from services.session_service import session_service


class LoginView(tk.Frame):
    """
    Modular login view card.
    
    Usage:
        login = LoginView(parent, on_login_success=lambda user: app.show_main_workspace())
        login.pack(fill="both", expand=True)
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_login_success: Optional[Callable[[str], Any]] = None,
        **kwargs,
    ):
        super().__init__(parent, bg=Colors.BG, **kwargs)
        self.on_login_success = on_login_success

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs login form card."""
        center_container = tk.Frame(self, bg=Colors.BG)
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(
            center_container,
            bg=Colors.CARD_BG,
            padx=40,
            pady=40,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        card.pack()

        # Logo / Header
        tk.Label(
            card,
            text="🔐 IT OPERATIONS",
            bg=Colors.CARD_BG,
            fg=Colors.PRIMARY,
            font=Fonts.HEADER,
        ).pack(pady=(0, 24))

        # Username Field
        tk.Label(
            card,
            text="Tên đăng nhập (Username)",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
        ).pack(anchor="w")

        available_users = session_service.get_available_operators()
        self.user_cb = ttk.Combobox(
            card,
            values=available_users,
            width=28,
            font=Fonts.MAIN,
        )
        self.user_cb.pack(pady=(5, 16), ipady=5)
        if available_users:
            self.user_cb.set(available_users[0])

        # Password Field
        tk.Label(
            card,
            text="Mật khẩu (Password)",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_DIM,
            font=Fonts.MAIN,
        ).pack(anchor="w")

        self.pwd_entry = tk.Entry(
            card,
            width=30,
            font=Fonts.MAIN,
            show="*",
            relief="flat",
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        self.pwd_entry.pack(pady=(5, 24), ipady=6)
        self.pwd_entry.bind("<Return>", lambda e: self.do_login())

        # Submit Button
        tk.Button(
            card,
            text="Đăng nhập",
            bg=Colors.PRIMARY,
            fg="white",
            font=Fonts.BOLD,
            relief="flat",
            cursor="hand2",
            command=self.do_login,
        ).pack(fill="x", ipady=8)

    def do_login(self) -> None:
        """Authenticates user through session_service."""
        username = self.user_cb.get().strip()
        password = self.pwd_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        ok, msg = session_service.authenticate(username, password)
        if ok:
            if self.on_login_success:
                self.on_login_success(username)
        else:
            messagebox.showerror("Đăng nhập thất bại", msg)
