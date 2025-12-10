# agenda/urls.py
from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.calendario, name='calendario'),         # /agenda/
    path('caso/<int:caso_id>/nueva/', views.AgendarCitaView.as_view(), name='agendar_caso'),    # /agenda/caso/1/nueva/
]
