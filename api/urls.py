from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Métriques globales
    path('stats/', views.DashboardStatsAPIView.as_view(), name='dashboard_stats'),

    # Espaces de travail par rôle
    path('workspace/direction/', views.DirectionWorkspaceAPIView.as_view(), name='workspace_direction'),
    path('workspace/enseignant/', views.EnseignantWorkspaceAPIView.as_view(), name='workspace_enseignant'),
    path('workspace/comptable/', views.ComptableWorkspaceAPIView.as_view(), name='workspace_comptable'),

    # Actions rapides interactives (DRF POST)
    path('actions/quick-note/', views.QuickNoteAPIView.as_view(), name='quick_note'),
    path('actions/quick-paiement/', views.QuickPaiementAPIView.as_view(), name='quick_paiement'),
]

