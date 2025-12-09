from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.lista_citas, name='lista'),
    path('nuevo/', views.crear_cita, name='crear'),
    path('<int:pk>/', views.detalle_cita, name='detalle'),
    path('<int:pk>/editar/', views.editar_cita, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_cita, name='eliminar'),
]
