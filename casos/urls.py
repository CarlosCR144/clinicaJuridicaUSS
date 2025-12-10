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
]