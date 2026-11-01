"""
Configuration package for IT Incident Logger.
Provides centralized settings, path resolution, and business constants.
"""
from config.settings import AppSettings, get_app_dir, get_db_path, setup_logging
from config.constants import (
    DETAIL_STRUCTURE,
    HMI_LINES,
    HMI_COLS,
    CURRENT_SITUATION_OPTIONS,
    DEFAULT_OPERATORS,
    SHIFT_OPTIONS,
    Colors,
    Fonts,
)

__all__ = [
    "AppSettings",
    "get_app_dir",
    "get_db_path",
    "setup_logging",
    "DETAIL_STRUCTURE",
    "HMI_LINES",
    "HMI_COLS",
    "CURRENT_SITUATION_OPTIONS",
    "DEFAULT_OPERATORS",
    "SHIFT_OPTIONS",
    "Colors",
    "Fonts",
]
