# personas/urls.py
from django.urls import path
from . import views

app_name = 'personas'

urlpatterns = [
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('personas/', views.lista_personas, name='lista_personas'),
    path('personas/nuevo/', views.crear_persona, name='crear_persona'),
    path('personas/<int:pk>/', views.detalle_persona, name='detalle_persona'),
    path('personas/editar/<int:pk>/', views.editar_persona, name='editar_persona'),
    path('personas/eliminar/<int:pk>/', views.eliminar_persona, name='eliminar_persona'),
    path('audit-log/', views.audit_log, name='audit_log'),
]
