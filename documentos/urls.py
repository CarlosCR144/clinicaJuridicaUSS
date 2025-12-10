# documentos/urls.py
from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    # path('subir/', views.subir_documento_general, name='subir_general'), # /documentos/subir/
    # path('subir/caso/<int:caso_id>/', views.subir_documento_caso, name='subir'),
    path('subir/<int:caso_id>/', views.SubirDocumentoView.as_view(), name='subir'),
    path('estado/<int:pk>/<str:accion>/', views.CambiarEstadoDocumentoView.as_view(), name='cambiar_estado'),
]
