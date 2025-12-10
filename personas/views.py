# ejemplos MUY básicos, solo para probar que las urls funcionan

# personas/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario, Persona
from .forms import PersonaForm, UsuarioForm
from .mixins import SoloDirectorMixin

# NO SE USA
def lista_usuarios(request):
    return render(request, 'personas/lista_usuarios.html', {'usuarios': []})

# NO SE USA
def crear_usuario(request):
    return render(request, 'personas/lista_usuarios.html')  # luego lo cambias a un form

# AUN SE MANTIENE LA URL
def detalle_usuario(request, pk):
    return render(request, 'personas/detalle_usuario.html', {})  # luego agregas datos

# --- Vistas para USUARIOS (Staff/Estudiantes) ---
class UsuarioListView(SoloDirectorMixin, LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'personas/lista_usuarios.html'
    context_object_name = 'usuarios'
    ordering = ['rol', 'username']

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

class PersonaCreateView(LoginRequiredMixin, CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'personas/form_persona.html'
    success_url = reverse_lazy('personas:lista_clientes')
    
    def form_valid(self, form):
        return super().form_valid(form)

class PersonaUpdateView(LoginRequiredMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'personas/form_persona.html'
    success_url = reverse_lazy('personas:lista_clientes')