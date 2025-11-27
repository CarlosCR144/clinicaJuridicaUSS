# agenda/urls.py
from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.calendario, name='calendario'),         # /agenda/
    path('nueva/', views.agendar_cita, name='agendar'),    # /agenda/nueva/
]
