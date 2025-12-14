from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Causa, Participante, Bitacora, RegistroCaso, RegistroCasoHistorial
from .forms import CausaForm, ParticipanteForm, RegistroCasoForm

# sirve para hacer consultas complejas
from django.db.models import Q
# sirve par decoradores de vistas basadas en clases
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from agenda.models import Cita
from documentos.models import Documento

from personas.mixins import SoloDirectorMixin, SoloStaffMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

class CausaListView(LoginRequiredMixin, ListView):
    model = Causa
    template_name = 'casos/lista_casos.html'
    context_object_name = 'casos'
    ordering = ['-fecha_ingreso']

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user

        if usuario.rol == 'estudiante':
            queryset = queryset.filter(responsable=usuario)
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(caratula__icontains=q) | queryset.filter(rol_rit__icontains=q)
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados_posibles'] = Causa.ESTADOS 
        return context

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
        
        context['documentos'] = self.object.documentos.all().order_by('orden_expediente')
        context['citas'] = self.object.citas.all().order_by('fecha_hora')
        
        # VALIDACIÓN DE INTEGRIDAD INTELIGENTE
        alertas_integridad = []
        
        for doc in context['documentos']:
            # Desempaquetamos la tupla (Estado, Hash Actual)
            es_valido, hash_actual = doc.verificar_integridad()
            
            if es_valido is False: # Hash no coincide (Modificado)
                
                # 1. Siempre mostramos la alerta visual en pantalla
                alertas_integridad.append({
                    'tipo': 'modificado',
                    'mensaje': f"El documento '{doc.nombre}' (Documento N° {doc.orden_expediente}) ha sido modificado externamente.",
                    'documento': doc
                })
                
                # 2. Lógica Anti-Spam de Bitácora
                # Solo registramos si es una modificación NUEVA (hash distinto al último error)
                if hash_actual != doc.hash_fallido:
                    Bitacora.objects.create(
                        causa=self.object,
                        usuario=self.request.user,
                        accion='nota', # O 'seguridad'
                        detalle=f"ALERTA SEGURIDAD CRÍTICA: Hash inconsistente en documento ID {doc.id}. (Nuevo hash detectado)"
                    )
                    
                    # Actualizamos la "memoria" del error
                    doc.hash_fallido = hash_actual
                    doc.save(update_fields=['hash_fallido'])

            elif es_valido is None: # Archivo borrado físicamente
                alertas_integridad.append({
                    'tipo': 'perdido',
                    'mensaje': f"ERROR CRÍTICO: El archivo físico del documento '{doc.nombre}' no se encuentra en el servidor.",
                    'documento': doc
                })
            
            elif es_valido is True:
                # Autocuración: Si el archivo se arregló (volvió a ser el original), limpiamos la bandera de error
                if doc.hash_fallido:
                    doc.hash_fallido = None
                    doc.save(update_fields=['hash_fallido'])

        context['alertas_integridad'] = alertas_integridad
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

@login_required
def buscar_casos(request):
    # Obtener el término de búsqueda desde los parámetros GET
    query = request.GET.get('query' or '').strip()

    # si no se escribe nada, devuelve campo vacio 
    causas = Causa.objects.none()
    documentos = Documento.objects.none()

    if query:
        #1. buscar en causas por RIT o carátula
        causas = Causa.objects.filter(
            Q(rol_rit__icontains=query) | Q(caratula__icontains=query)
        )

        #2. rol estudiante
        if request.user.rol == 'estudiante':
            causas = causas.filter(responsable= request.user)

        #3. si el usuario es estudiante, solo ve sus causas
        if query.isdigit():
            # si tiene numeros, asume que busca  el ID de un documento
            documentos = Documento.objects.filter(id=int(query)).select_related('causa')

            # estudiante solo ve documentos de sus causas
            if request.user.rol == 'estudiante':
                documentos = Documento.filter(causa__responsable = request.user)
    
    return render(request, 'casos/buscar_casos.html',{
        'query':query,
        'causas':causas,
        'documentos':documentos,
    })

class RegistroCasoEditView(LoginRequiredMixin, View):
    """
    Permite crear o editar el registro textual (hoja viva)
    de una causa.
    """

    def dispatch(self, request, *args, **kwargs):
        causa = get_object_or_404(Causa, pk=kwargs['pk'])

        # bloqueo si el caso está cerrado o archivado
        if causa.estado in ['archivada', 'con_sentencia']:
            messages.error(
                request,
                "El registro interno está cerrado porque el caso fue finalizado."
            )
            return redirect('casos:detalle', pk=causa.pk)

        # Permisos por rol
        if request.user.rol in ['director', 'supervisor']:
            return super().dispatch(request, *args, **kwargs)

        if request.user.rol == 'estudiante' and causa.responsable == request.user:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request,"No tienes permisos para editar el registro de este caso.")
        return redirect('casos:detalle', pk=causa.pk)


    def get(self, request,pk):
        causa = get_object_or_404(Causa, pk=pk)

        # 1. obtener o crear el registro
        registro, creado = RegistroCaso.objects.get_or_create(causa=causa)

        # 2. Crear el formulario con el contenido actual
        form = RegistroCasoForm(instance=registro)

        return render(request, 'casos/registro_caso_form.html',{
            'causa':causa,
            'form':form,
        })
    
    #guardar cambios
    def post(self,request,pk):
        causa = get_object_or_404(Causa, pk=pk)
        registro, _ = RegistroCaso.objects.get_or_create(causa=causa)
        contenido_anterior = registro.contenido or ''

        form = RegistroCasoForm(request.POST, instance=registro) #sd muestra el texto guardado y no se crea uno nuevo,
        #ya que representa el registro en especifico

        if form.is_valid():
           nuevo_registro = form.save(commit=False)
           nuevo_contenido = nuevo_registro.contenido or ''

           # Solo guardar historial si hubo cambios
           if nuevo_contenido != (contenido_anterior or "").strip():
                # Guardar snapshot en historial
                RegistroCasoHistorial.objects.create(
                     causa=causa,
                     contenido=contenido_anterior,
                     creado_por=request.user
                )

                # Actualizar el registro principal
                nuevo_registro.actualizado_por = request.user
                nuevo_registro.save()

                Bitacora.objects.create(
                    causa=causa,
                    usuario=request.user,
                    accion='nota',
                    detalle="Se actualizó el registro interno del caso."
                )

                messages.success(request, 'Registro del caso ha sido guardado correctamente')
                return redirect('casos:detalle', pk=causa.pk)
            
        return render(request, 'casos/registro_caso_form.html',{
            'causa':causa,
            'form':form,
        })
    
class RegistroCasoHistorialView(LoginRequiredMixin, ListView):
    def get(self, request, pk):
        causa = get_object_or_404(Causa, pk=pk)

        # Solo director, supervisor pueden ver historial
        if request.user.rol in ['director', 'supervisor']:
            pass
        # Estudiante responsable del caso
        elif request.user.rol == 'estudiante' and causa.responsable == request.user:
            pass
        else:
            messages.error(request, "No tienes permisos para ver el historial del registro de este caso")
            return redirect('casos:detalle', pk=causa.pk)    

        historial = causa.registro_historial.all()

        return render(request, 'casos/registro_caso_historial.html',{
            'causa':causa,
            'historial':historial,
        })
    
