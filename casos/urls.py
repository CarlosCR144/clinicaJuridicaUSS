# casos/urls.py
from django.urls import path
from . import views

app_name = 'casos'

urlpatterns = [
    path('', views.lista_casos, name='lista'),             # /casos/
    path('nuevo/', views.crear_caso, name='crear'),        # /casos/nuevo/
    path('<int:pk>/', views.detalle_caso, name='detalle'), # /casos/1/
    path('buscar/', views.buscar_casos, name='buscar'),  # /casos/buscar/
]
