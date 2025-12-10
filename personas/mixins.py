from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

class RolRequiredMixin(UserPassesTestMixin):
    roles_permitidos = []

    def test_func(self):
        usuario = self.request.user
        # 1. El usuario debe estar logueado
        if not usuario.is_authenticated:
            return False
        
        if usuario.is_superuser or usuario.rol == 'admin':
            return True
            
        return usuario.rol in self.roles_permitidos

    def handle_no_permission(self):
        from django.contrib import messages
        messages.error(self.request, "No tienes permisos para realizar esta acción.")
        return redirect('home')

# --- Mixins Específicos ---

class SoloDirectorMixin(RolRequiredMixin):
    """Solo Director y Admin pueden acceder"""
    roles_permitidos = ['director']

class SoloStaffMixin(RolRequiredMixin):
    """Director, Supervisor y Secretaria (Administrativos)"""
    roles_permitidos = ['director', 'supervisor', 'secretaria']

class SoloSupervisorMixin(RolRequiredMixin):
    """Solo Supervisores"""
    roles_permitidos = ['supervisor']

class SoloEstudianteMixin(RolRequiredMixin):
    """Solo Estudiantes"""
    roles_permitidos = ['estudiante']