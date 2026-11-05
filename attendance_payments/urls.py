from django.urls import path
from . import views

app_name = 'attendance_payments'

urlpatterns = [
    # Absences
    path('absences/', views.absence_list, name='absence_list'),
    path('absences/enregistrer/', views.absence_create, name='absence_create'),
    path('absences/<int:pk>/modifier/', views.absence_edit, name='absence_edit'),
    path('absences/<int:pk>/supprimer/', views.absence_delete, name='absence_delete'),

    # Paiements & Frais
    path('paiements/', views.paiement_list, name='paiement_list'),
    path('paiements/nouveau/', views.paiement_create, name='paiement_create'),
    path('paiements/<int:pk>/modifier/', views.paiement_edit, name='paiement_edit'),
    path('paiements/<int:pk>/supprimer/', views.paiement_delete, name='paiement_delete'),
    path('paiements/suivi/', views.suivi_paiements, name='suivi_paiements'),

    # Communication & Relances (Action Web + API)
    path('paiements/relance/<int:pk>/', views.relance_paiement_view, name='relance_paiement'),
    path('api/relance/<int:inscription_id>/', views.api_envoyer_relance, name='api_relance'),
    path('api/convocation/<int:inscription_id>/', views.api_envoyer_convocation, name='api_convocation'),
]
