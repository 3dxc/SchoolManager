from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Élèves
    path('', views.eleve_list, name='eleve_list'),
    path('creer/', views.eleve_create, name='eleve_create'),
    path('<int:pk>/', views.eleve_detail, name='eleve_detail'),
    path('<int:pk>/modifier/', views.eleve_edit, name='eleve_edit'),
    path('<int:pk>/supprimer/', views.eleve_delete, name='eleve_delete'),
    # Parents
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/creer/', views.parent_create, name='parent_create'),
    path('parents/<int:pk>/modifier/', views.parent_edit, name='parent_edit'),
    path('parents/<int:pk>/supprimer/', views.parent_delete, name='parent_delete'),
    # Inscriptions
    path('inscriptions/', views.inscription_list, name='inscription_list'),
    path('inscriptions/creer/', views.inscription_create, name='inscription_create'),
    path('inscriptions/<int:pk>/modifier/', views.inscription_edit, name='inscription_edit'),
    path('inscriptions/<int:pk>/supprimer/', views.inscription_delete, name='inscription_delete'),
]
