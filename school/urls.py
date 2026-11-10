from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    # Établissements
    path('etablissements/', views.etablissement_list, name='etablissement_list'),
    path('etablissements/creer/', views.etablissement_create, name='etablissement_create'),
    path('etablissements/<int:pk>/modifier/', views.etablissement_edit, name='etablissement_edit'),
    path('etablissements/<int:pk>/supprimer/', views.etablissement_delete, name='etablissement_delete'),
    # Années scolaires
    path('annees/', views.annee_list, name='annee_list'),
    path('annees/creer/', views.annee_create, name='annee_create'),
    path('annees/<int:pk>/modifier/', views.annee_edit, name='annee_edit'),
    path('annees/<int:pk>/supprimer/', views.annee_delete, name='annee_delete'),
    # Classes
    path('classes/', views.classe_list, name='classe_list'),
    path('classes/creer/', views.classe_create, name='classe_create'),
    path('classes/<int:pk>/modifier/', views.classe_edit, name='classe_edit'),
    path('classes/<int:pk>/supprimer/', views.classe_delete, name='classe_delete'),
    # Matières
    path('matieres/', views.matiere_list, name='matiere_list'),
    path('matieres/creer/', views.matiere_create, name='matiere_create'),
    path('matieres/<int:pk>/modifier/', views.matiere_edit, name='matiere_edit'),
    path('matieres/<int:pk>/supprimer/', views.matiere_delete, name='matiere_delete'),
    # Signalements
    path('signalement/', views.signalement_create, name='signalement_create'),
]
