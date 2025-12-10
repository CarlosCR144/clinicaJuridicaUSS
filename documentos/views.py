from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages

from .models import Documento
from .forms import DocumentoForm
from casos.models import Causa, Bitacora

class SubirDocumentoView(LoginRequiredMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'documentos/subir_documento.html'

    def dispatch(self, request, *args, **kwargs):
        # Capturamos la causa desde la URL antes de procesar nada
        self.causa = get_object_or_404(Causa, pk=self.kwargs['caso_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caso'] = self.causa
        return context

    def form_valid(self, form):
        # 1. Completar datos automáticos del documento
        documento = form.save(commit=False)
        documento.causa = self.causa
        documento.subido_por = self.request.user
        documento.save() # Aquí se dispara la lógica del modelo (Foliación + Hash)

        # 2. LOG DE BITÁCORA (TRAZABILIDAD)
        Bitacora.objects.create(
            causa=self.causa,
            usuario=self.request.user,
            accion='archivo', # 'archivo' debe estar en tus choices de Bitacora
            detalle=f"Se subió documento: {documento.nombre} (Folio {documento.folio})"
        )

        messages.success(self.request, "Documento subido y foliado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        # Volver al detalle del caso
        return reverse('casos:detalle', kwargs={'pk': self.causa.pk})

# Funciones antiguas placeholders
def lista_documentos(request): return render(request, 'documentos/lista_documentos.html')
def subir_documento_general(request): return render(request, 'documentos/subir_documento.html')
def subir_documento_caso(request, caso_id): return render(request, 'documentos/subir_documento.html')