from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Enseignants
    path('enseignants/', views.enseignant_list, name='enseignant_list'),
    path('enseignants/creer/', views.enseignant_create, name='enseignant_create'),
    path('enseignants/<int:pk>/modifier/', views.enseignant_edit, name='enseignant_edit'),
    path('enseignants/<int:pk>/supprimer/', views.enseignant_delete, name='enseignant_delete'),
    # Affectations
    path('affectations/', views.affectation_list, name='affectation_list'),
    path('affectations/creer/', views.affectation_create, name='affectation_create'),
    path('affectations/<int:pk>/supprimer/', views.affectation_delete, name='affectation_delete'),
    # Notes
    path('notes/', views.note_list, name='note_list'),
    path('notes/saisir/', views.note_create, name='note_create'),
    path('notes/<int:pk>/modifier/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/supprimer/', views.note_delete, name='note_delete'),
    # Bulletin
    path('bulletin/<int:inscription_pk>/', views.bulletin, name='bulletin'),
    path('bulletin/<int:inscription_pk>/notifier/', views.notifier_bulletin, name='notifier_bulletin'),
]
