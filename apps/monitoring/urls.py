from django.urls import path
from .views import (
    DashboardStatsView,
    SecurityAlertView,
    MassControlView,
    ReportViolationView,
    monitoring_page_view,
    OnlineUsersDetailView,
    GlobalSettingsView,
    LiveProctoringView
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('stats/online/', OnlineUsersDetailView.as_view(), name='online-users-detail'),
    path('alerts/', SecurityAlertView.as_view(), name='security-alerts'),
    path('control/', MassControlView.as_view(), name='mass-control'),
    path('report/', ReportViolationView.as_view(), name='report-violation'),
    path('settings/', GlobalSettingsView.as_view(), name='global-settings'),
    path('live/', LiveProctoringView.as_view(), name='live-proctoring'),
]
