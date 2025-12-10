# personas/urls.py
from django.urls import path
from . import views

app_name = 'personas'

urlpatterns = [
    # Gestión de Usuarios
    path('usuarios/', views.UsuarioListView.as_view(), name='lista_usuarios'),
    path('usuarios/nuevo/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),

    # Gestión de Clientes (Personas Atendidas)
    path('clientes/', views.PersonaListView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', views.PersonaCreateView.as_view(), name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.PersonaUpdateView.as_view(), name='editar_cliente'),
]
