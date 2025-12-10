from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Causa, Participante, Bitacora
from .forms import CausaForm, ParticipanteForm

from django.utils import timezone
from agenda.models import Cita
from documentos.models import Documento

from personas.mixins import SoloDirectorMixin, SoloStaffMixin
from django.views import View

class CausaListView(LoginRequiredMixin, ListView):
    model = Causa
    template_name = 'casos/lista_casos.html'
    context_object_name = 'casos'
    ordering = ['-fecha_ingreso']

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user

        # Si es Estudiante, SOLO ve casos donde es responsable
        if usuario.rol == 'estudiante':
            queryset = queryset.filter(responsable=usuario)
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(caratula__icontains=q) | queryset.filter(rol_rit__icontains=q)
        
        return queryset

class CausaCreateView(SoloDirectorMixin, LoginRequiredMixin, CreateView):
    model = Causa
    form_class = CausaForm
    template_name = 'casos/crear_caso.html'
    success_url = reverse_lazy('casos:lista')

    def form_valid(self, form):
        if not form.instance.responsable:
            form.instance.responsable = self.request.user
            
        response = super().form_valid(form)
        
        Bitacora.objects.create(
            causa=self.object,
            usuario=self.request.user,
            accion='creacion',
            detalle=f"Apertura de expediente RIT: {self.object.rol_rit}. Asignado a: {self.object.responsable.get_full_name()}"
        )
        
        messages.success(self.request, f"Causa creada y asignada a {self.object.responsable}.")
        return response

class CausaUpdateView(SoloDirectorMixin, LoginRequiredMixin, UpdateView):
    model = Causa
    form_class = CausaForm
    template_name = 'casos/crear_caso.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar / Reasignar Caso"
        return context

    def form_valid(self, form):
        # Detectar si cambió el responsable para anotarlo en la bitácora
        if 'responsable' in form.changed_data:
            nuevo_resp = form.instance.responsable
            Bitacora.objects.create(
                causa=self.object,
                usuario=self.request.user,
                accion='actualizacion',
                detalle=f"Se reasignó el caso a: {nuevo_resp.get_full_name()}"
            )
            
        messages.success(self.request, "Caso actualizado correctamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('casos:detalle', kwargs={'pk': self.object.pk})

class CausaDetailView(LoginRequiredMixin, DetailView):
    model = Causa
    template_name = 'casos/detalle_caso.html'
    context_object_name = 'caso'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if request.user.rol == 'estudiante':
            if self.object.responsable != request.user:
                messages.error(request, "No tienes permisos para ver este caso.")
                return redirect('home')
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['documentos'] = self.object.documentos.all().order_by('folio')
        
        context['citas'] = self.object.citas.all().order_by('fecha_hora')
        
        return context

# -------- Participantes
class ParticipanteCreateView(LoginRequiredMixin, CreateView):
    model = Participante
    form_class = ParticipanteForm
    template_name = 'casos/form_participante.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['caso_id'] = self.kwargs['caso_id']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caso'] = get_object_or_404(Causa, pk=self.kwargs['caso_id'])
        return context

    def form_valid(self, form):
        form.instance.causa_id = self.kwargs['caso_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('casos:detalle', kwargs={'pk': self.kwargs['caso_id']})

def home(request):
    context = {}
    
    if request.user.is_authenticated:
        usuario = request.user
        
        # --- 1. KPIs ---
        qs_casos = Causa.objects.exclude(estado='archivada')
        
        # Si es estudiante, solo contamos SUS casos activos
        if usuario.rol == 'estudiante':
            qs_casos = qs_casos.filter(responsable=usuario)
            
        context['total_casos_activos'] = qs_casos.count()
        
        # --- 2. Citas para HOY ---
        ahora = timezone.localtime(timezone.now())
        inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_hoy = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        qs_citas = Cita.objects.filter(fecha_hora__range=(inicio_hoy, fin_hoy))
        
        # Si es estudiante, solo ve SUS citas
        if usuario.rol == 'estudiante':
            qs_citas = qs_citas.filter(responsable=usuario)
            
        context['citas_hoy'] = qs_citas.order_by('fecha_hora')
        
        # --- 3. Documentos ---
        # Si es estudiante, solo ve docs de SUS casos
        qs_docs = Documento.objects.select_related('causa')
        if usuario.rol == 'estudiante':
            qs_docs = qs_docs.filter(causa__responsable=usuario)
            
        context['docs_recientes'] = qs_docs.order_by('-fecha_subida')[:5]

    return render(request, 'home.html', context)

class CambiarEstadoCasoView(LoginRequiredMixin, View):
    def post(self, request, pk, accion):
        caso = get_object_or_404(Causa, pk=pk)
        usuario = request.user
        nuevo_estado = None
        descripcion_cambio = ""

        # --- Lógica de Transiciones ---
        
        # 1. ADMISIBILIDAD (Solo Director)
        if accion == 'admitir':
            if usuario.rol != 'director':
                messages.error(request, "Solo el Director puede admitir causas.")
                return redirect('casos:detalle', pk=pk)
            
            nuevo_estado = 'en_tramite'
            descripcion_cambio = "Causa declarada ADMISIBLE. Pasa a tramitación."

        elif accion == 'rechazar':
            if usuario.rol != 'director':
                messages.error(request, "Solo el Director puede rechazar causas.")
                return redirect('casos:detalle', pk=pk)
            
            nuevo_estado = 'archivada'
            descripcion_cambio = "Causa declarada INADMISIBLE. Se archiva el expediente."

        # 2. CIERRE / SENTENCIA (Supervisor o Director)
        elif accion == 'finalizar':
            if usuario.rol not in ['director', 'supervisor']:
                messages.error(request, "No tienes permisos para finalizar causas.")
                return redirect('casos:detalle', pk=pk)
            
            nuevo_estado = 'con_sentencia'
            descripcion_cambio = "Causa finalizada con sentencia/resolución."
            
        elif accion == 'archivar':
            if usuario.rol not in ['director', 'supervisor']:
                messages.error(request, "No tienes permisos para archivar causas.")
                return redirect('casos:detalle', pk=pk)
            
            nuevo_estado = 'archivada'
            descripcion_cambio = "Causa archivada administrativamente."

        # --- Ejecución del Cambio ---
        if nuevo_estado:
            # 1. Actualizar estado
            estado_anterior = caso.get_estado_display()
            caso.estado = nuevo_estado
            caso.save()

            # 2. Registro en Bitácora
            Bitacora.objects.create(
                causa=caso,
                usuario=usuario,
                accion='actualizacion',
                detalle=f"{descripcion_cambio} (De '{estado_anterior}' a '{caso.get_estado_display()}')"
            )
            
            messages.success(request, f"Estado actualizado: {caso.get_estado_display()}")
        
        return redirect('casos:detalle', pk=pk)

# Funciones antiguas
def lista_casos(request): return render(request, 'casos/lista_casos.html')
def crear_caso(request): return render(request, 'casos/crear_caso.html')
def detalle_caso(request, pk): return render(request, 'casos/detalle_caso.html')