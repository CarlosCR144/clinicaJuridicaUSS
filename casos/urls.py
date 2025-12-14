from django.urls import path
from . import views

app_name = 'casos'

urlpatterns = [
    path('', views.CausaListView.as_view(), name='lista'),
    path('nuevo/', views.CausaCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.CausaDetailView.as_view(), name='detalle'),
    path('<int:caso_id>/participantes/nuevo/', views.ParticipanteCreateView.as_view(), name='crear_participante'),
    path('<int:pk>/estado/<str:accion>/', views.CambiarEstadoCasoView.as_view(), name='cambiar_estado'),
    path('<int:pk>/editar/', views.CausaUpdateView.as_view(), name='editar'),
    path('buscar_casos/', views.buscar_casos, name='buscar_casos'),
    path('<int:pk>/registro/', views.RegistroCasoEditView.as_view(), name='editar_registro'),
    path('<int:pk>/registro/historial/', views.RegistroCasoHistorialView.as_view(), name='historial_registro'),
]