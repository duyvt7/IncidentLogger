"""
Application Settings and Path Resolution Module.

Handles application configuration, dynamic database path resolution
(compatible with both script execution and PyInstaller bundled .exe),
and centralized logging setup.
"""
from dataclasses import dataclass
from pathlib import Path
import logging
import sys


def get_app_dir() -> Path:
    """
    Returns the root directory of the application.
    If packaged with PyInstaller (sys.frozen), returns the directory of the executable.
    Otherwise, returns the parent directory of the config folder (project root).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_db_path() -> Path:
    """
    Dynamically resolves the SQLite database path:
    1. Checks for 'it_errors.db' in the app directory.
    2. Checks for 'it_errors.db' in 'dist/' directory.
    3. Fallback: 'dist/it_errors.db' if 'dist' folder exists, otherwise root 'it_errors.db'.
    """
    app_dir = get_app_dir()
    candidates = [
        app_dir / "it_errors.db",
        app_dir / "dist" / "it_errors.db",
    ]
    for path in candidates:
        if path.exists():
            return path

    return candidates[1] if (app_dir / "dist").is_dir() else candidates[0]


def setup_logging(log_level: int = logging.INFO) -> None:
    """
    Sets up logging to both console and an 'app.log' file in the application directory.
    """
    app_dir = get_app_dir()
    log_file = app_dir / "app.log"

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    logging.info("Logging initialized. App Directory: %s", app_dir)


@dataclass(frozen=True)
class AppSettings:
    """Centralized application settings."""
    app_title: str = "IT Operations Dashboard"
    window_geometry: str = "1300x820"
    min_width: int = 1000
    min_height: int = 650
    default_dept: str = "IT"
    default_section: str = "IT Management"
    
    # Extensible Auth Flag:
    # Set to False to open application directly without login barrier.
    # Set to True when ready to enforce authentication and user login screen.
    auth_enabled: bool = False

