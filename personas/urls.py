# personas/urls.py
from django.urls import path
from . import views

app_name = 'personas'

urlpatterns = [
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/', views.detalle_usuario, name='detalle_usuario'),
]
