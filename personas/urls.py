# personas/urls.py
from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'personas'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='personas:lista_clientes'), name='index'),
    
    # Gestión de Usuarios
    path('usuarios/', views.UsuarioListView.as_view(), name='lista_usuarios'),
    path('usuarios/nuevo/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.UsuarioSoftDeleteView.as_view(), name='eliminar_usuario'),
    path('usuarios/restaurar/<int:pk>/', views.UsuarioRestoreView.as_view(), name='restaurar_usuario'),

    # Gestión de Clientes (Personas Atendidas)
    path('clientes/', views.PersonaListView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', views.PersonaCreateView.as_view(), name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.PersonaUpdateView.as_view(), name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.PersonaSoftDeleteView.as_view(), name='eliminar_cliente'),
    path('clientes/restaurar/<int:pk>/', views.PersonaRestoreView.as_view(), name='restaurar_cliente'),
]
