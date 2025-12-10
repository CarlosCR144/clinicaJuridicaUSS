# ejemplos MUY básicos, solo para probar que las urls funcionan

# personas/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario, Persona
from .forms import PersonaForm, UsuarioForm
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

# --- Vistas para CLIENTES (Personas Atendidas) ---
class PersonaListView(LoginRequiredMixin, ListView):
    model = Persona
    template_name = 'personas/lista_clientes.html'
    context_object_name = 'personas'
    ordering = ['-fecha_registro']

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