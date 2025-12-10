from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .models import Documento
from .forms import DocumentoForm
from casos.models import Causa, Bitacora
from personas.mixins import RolRequiredMixin

class SubirDocumentoView(RolRequiredMixin, LoginRequiredMixin, CreateView):
    roles_permitidos = ['director', 'supervisor', 'estudiante']
    model = Documento
    form_class = DocumentoForm
    template_name = 'documentos/subir_documento.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.causa = get_object_or_404(Causa, pk=self.kwargs['caso_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caso'] = self.causa
        return context

    def form_valid(self, form):
        documento = form.save(commit=False)
        documento.causa = self.causa
        documento.subido_por = self.request.user
        documento.save()

        Bitacora.objects.create(
            causa=self.causa,
            usuario=self.request.user,
            accion='archivo',
            detalle=f"Se subió documento: {documento.nombre} (Folio {documento.folio}) - Estado: {documento.get_estado_display()}"
        )

        messages.success(self.request, "Documento subido. Queda pendiente de revisión por el Supervisor.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('casos:detalle', kwargs={'pk': self.causa.pk})

class CambiarEstadoDocumentoView(RolRequiredMixin, LoginRequiredMixin, View):
    roles_permitidos = ['director', 'supervisor']
    def post(self, request, pk, accion):
        doc = get_object_or_404(Documento, pk=pk)
        
        # Validar permisos extra si quieres ser estricto (solo supervisor/director)
        if request.user.rol not in ['director', 'supervisor']:
             messages.error(request, "No tienes permisos para aprobar documentos.")
             return redirect('casos:detalle', pk=doc.causa.pk)

        if accion == 'aprobar':
            doc.estado = 'aprobado'
            doc.aprobado_por = request.user
            doc.fecha_aprobacion = timezone.now()
            doc.observaciones_rechazo = "" # Limpiamos rechazos previos si los hubo
            msg = f"Documento '{doc.nombre}' APROBADO."
            
        elif accion == 'rechazar':
            doc.estado = 'rechazado'
            # Capturamos el motivo desde un input en el template (ver Paso 3)
            motivo = request.POST.get('motivo_rechazo', 'Sin motivo especificado')
            doc.observaciones_rechazo = motivo
            msg = f"Documento '{doc.nombre}' RECHAZADO."

        doc.save()

        # Registro en Bitácora
        Bitacora.objects.create(
            causa=doc.causa,
            usuario=request.user,
            accion='actualizacion', # O 'nota'
            detalle=f"Revisión Documento (Folio {doc.folio}): {doc.get_estado_display()}. {doc.observaciones_rechazo}"
        )

        messages.success(request, msg)
        return redirect('casos:detalle', pk=doc.causa.pk)
