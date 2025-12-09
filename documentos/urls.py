# documentos/urls.py
from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('', views.lista_documentos, name='lista'),                      # /documentos/
    path('subir/', views.subir_documento_general, name='subir_general'), # /documentos/subir/
    path('generar_notificacion/<int:doc_id>/', views.generar_notificacion, name='generar_notificacion'),
    path('descargar/<uuid:token>/', views.descargar_documento, name='descargar'),
]
