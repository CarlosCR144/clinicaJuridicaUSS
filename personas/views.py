# ejemplos MUY básicos, solo para probar que las urls funcionan

# personas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario, Persona
from .forms import PersonaForm, UsuarioForm
from django.views import View
from .mixins import SoloDirectorMixin, SoloStaffMixin, RolRequiredMixin

# --- Vistas para USUARIOS (Staff/Estudiantes) ---
class UsuarioListView(SoloDirectorMixin, LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'personas/lista_usuarios.html'
    context_object_name = 'usuarios'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por Rol desde la URL (?rol=estudiante)
        rol_filter = self.request.GET.get('rol')
        if rol_filter:
            queryset = queryset.filter(rol=rol_filter)
            
        return queryset.order_by('rol', 'username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos el rol actual para activar la pestaña correspondiente
        context['rol_actual'] = self.request.GET.get('rol', '')
        return context

class UsuarioCreateView(SoloDirectorMixin, LoginRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'personas/form_usuario.html'
    success_url = reverse_lazy('personas:lista_usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Registrar Nuevo Usuario"
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

class UsuarioUpdateView(SoloDirectorMixin, LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'personas/form_usuario.html'
    success_url = reverse_lazy('personas:lista_usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f"Editar Usuario: {self.object.username}"
        return context

class UsuarioSoftDeleteView(SoloDirectorMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        usuario_a_borrar = get_object_or_404(Usuario, pk=pk)
        
        # Protección: No te puedes borrar a ti mismo
        if usuario_a_borrar == request.user:
            messages.error(request, "No puedes eliminar tu propia cuenta.")
            return redirect('personas:lista_usuarios')

        # Acción: Toggle o Desactivar
        if usuario_a_borrar.is_active:
            usuario_a_borrar.is_active = False
            usuario_a_borrar.save()
            messages.success(request, f"Usuario {usuario_a_borrar.username} desactivado correctamente.")
        else:
            messages.warning(request, "El usuario ya estaba inactivo.")
            
        return redirect('personas:lista_usuarios')

class UsuarioRestoreView(SoloDirectorMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if not usuario.is_active:
            usuario.is_active = True
            usuario.save()
            messages.success(request, f"Usuario {usuario.username} restaurado y activo nuevamente.")
        return redirect('personas:lista_usuarios')

# --- Vistas para CLIENTES (Personas Atendidas) ---
class PersonaListView(LoginRequiredMixin, ListView):
    model = Persona
    template_name = 'personas/lista_clientes.html'
    context_object_name = 'personas'
    ordering = ['-fecha_registro']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.rol == 'estudiante':
            queryset = queryset.filter(is_active=True)
        return queryset

class PersonaCreateView(RolRequiredMixin, LoginRequiredMixin, CreateView):
    roles_permitidos = ['director', 'secretaria', 'admin']
    model = Persona
    form_class = PersonaForm
    template_name = 'personas/form_persona.html'
    success_url = reverse_lazy('personas:lista_clientes')
    
    def form_valid(self, form):
        return super().form_valid(form)

class PersonaUpdateView(RolRequiredMixin, LoginRequiredMixin, UpdateView):
    roles_permitidos = ['director', 'secretaria', 'admin']
    model = Persona
    form_class = PersonaForm
    template_name = 'personas/form_persona.html'
    success_url = reverse_lazy('personas:lista_clientes')

class PersonaSoftDeleteView(SoloStaffMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        persona = get_object_or_404(Persona, pk=pk)
        
        if persona.is_active:
            persona.is_active = False
            persona.save()
            messages.success(request, f"Cliente {persona.nombres} desactivado.")
        
        return redirect('personas:lista_clientes')

class PersonaRestoreView(SoloStaffMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        persona = get_object_or_404(Persona, pk=pk)
        if not persona.is_active:
            persona.is_active = True
            persona.save()
            messages.success(request, f"Cliente {persona.nombres} restaurado.")
        return redirect('personas:lista_clientes')