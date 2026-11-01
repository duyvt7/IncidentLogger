"""
IT Operations Dashboard - Main Entry Point.

Clean Application Controller initializing database, styles, shift header,
and operational tabs (Dashboard, Detail, HMI Checking).
"""
import logging
import tkinter as tk
from tkinter import ttk

from config.settings import AppSettings, setup_logging, get_app_dir
from config.constants import Colors
from database.schema import init_db
from ui.styles import apply_app_styles
from ui.views.header_view import HeaderView
from ui.views.dashboard_view import DashboardView
from ui.views.detail_view import DetailView
from ui.views.hmi_view import HmiView
from ui.views.daily_inspection_view import DailyInspectionView
from ui.views.login_view import LoginView

logger = logging.getLogger(__name__)


class ITOperationsApp(tk.Tk):
    """
    Main Application Window orchestrating views, tabs, and shared state.
    """

    def __init__(self, settings: AppSettings = None):
        super().__init__()
        self.settings = settings or AppSettings()

        # 1. Setup Logging & Database
        setup_logging()
        init_db()

        # 2. Window Properties
        self.title(self.settings.app_title)
        self.geometry(self.settings.window_geometry)
        self.minsize(self.settings.min_width, self.settings.min_height)
        self.configure(bg=Colors.BG)

        # 3. Load App Icon if available
        self._set_app_icon()

        # 4. Apply ttk theme styles
        apply_app_styles(self)

        # 5. Routing: Check if Authentication is enforced
        if self.settings.auth_enabled:
            self._show_login_screen()
        else:
            self.build_main_workspace()

    def _set_app_icon(self) -> None:
        """Sets window and taskbar icon."""
        app_dir = get_app_dir()
        icon_path = app_dir / "app_icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception as exc:
                logger.debug("Could not load iconbitmap: %s", exc)

    def _show_login_screen(self) -> None:
        """Displays login view (used when auth_enabled is True)."""
        self.login_view = LoginView(
            self,
            on_login_success=self._on_login_success,
        )
        self.login_view.pack(fill="both", expand=True)

    def _on_login_success(self, username: str) -> None:
        """Callback after successful authentication."""
        if hasattr(self, "login_view"):
            self.login_view.destroy()
        self.build_main_workspace()

    def build_main_workspace(self) -> None:
        """Builds the main workspace: Header bar and Notebook tab panels."""
        self.main_container = tk.Frame(self, bg=Colors.BG)
        self.main_container.pack(fill="both", expand=True)

        # 1. Shift Header Bar
        self.header_view = HeaderView(self.main_container)
        self.header_view.pack(fill="x", padx=16, pady=(12, 6))

        # 2. Tabbed Notebook
        notebook = ttk.Notebook(self.main_container)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Tab 1: Dashboard
        self.dashboard_view = DashboardView(notebook)
        notebook.add(self.dashboard_view, text="  📊 Dashboard  ")

        # Tab 3: HMI Checking (Instantiate before DetailView so detail can grab HMI data)
        self.hmi_view = HmiView(notebook)

        # Tab 2: Detail
        self.detail_view = DetailView(
            notebook,
            get_shift_info_cb=self.header_view.get_shift_info,
            get_hmi_data_cb=self.hmi_view.get_hmi_data,
            on_data_changed_cb=self.dashboard_view.refresh_statistics,
        )
        notebook.add(self.detail_view, text="  📝 2. Detail  ")
        notebook.add(self.hmi_view, text="  ✅ 3. HMI Checking  ")

        # Tab 4: Daily Inspection
        self.daily_view = DailyInspectionView(
            notebook,
            get_shift_info_cb=self.header_view.get_shift_info,
        )
        notebook.add(self.daily_view, text="  📋 4. Daily Inspection  ")

        logger.info("Main workspace loaded successfully.")


def main() -> None:
    """Application entry point."""
    app = ITOperationsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
