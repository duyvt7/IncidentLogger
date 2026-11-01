"""
Views package for IT Incident Logger.
Contains individual views for Header, Dashboard, Detail, HMI, and optional Login.
"""
from ui.views.header_view import HeaderView
from ui.views.dashboard_view import DashboardView
from ui.views.detail_view import DetailView
from ui.views.hmi_view import HmiView
from ui.views.login_view import LoginView

__all__ = [
    "HeaderView",
    "DashboardView",
    "DetailView",
    "HmiView",
    "LoginView",
]

