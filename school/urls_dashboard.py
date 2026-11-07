from django.urls import path
from . import views_dashboard

urlpatterns = [
    path('', views_dashboard.dashboard, name='dashboard'),
    path('statistiques/export/csv/', views_dashboard.export_stats_csv, name='export_stats_csv'),
]
