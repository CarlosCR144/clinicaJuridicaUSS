# clinica_juridica/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página de inicio
    path(
        '',
        TemplateView.as_view(template_name='home.html'),
        name='home'
    ),

    # Autenticación básica
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='personas/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # Apps del proyecto
    path('personas/', include(('personas.urls', 'personas'), namespace='personas')),
    path('casos/', include(('casos.urls', 'casos'), namespace='casos')),
    path('agenda/', include(('agenda.urls', 'agenda'), namespace='agenda')),
    path('documentos/', include(('documentos.urls', 'documentos'), namespace='documentos')),
]
