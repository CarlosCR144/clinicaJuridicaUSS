# documentos/urls.py
from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('', views.lista_documentos, name='lista'),                      # /documentos/
    path('subir/', views.subir_documento_general, name='subir_general'), # /documentos/subir/
    path('subir/caso/<int:caso_id>/', views.subir_documento_caso, name='subir'),
]
