from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils import timezone
import os

from .models import Documento, Notificacion
from .forms import DocumentoForm
from personas.utils import log_action
from django.contrib.auth.decorators import login_required


@login_required
def lista_documentos(request):
    documentos = Documento.objects.select_related('causa').all().order_by('-creado_en')
    return render(request, 'documentos/lista_documentos.html', {'documentos': documentos})


@login_required
def subir_documento_general(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save()
            log_action(request.user, 'SUBIR', 'Documento', documento.id, f'Subido documento: {documento.titulo}')
            messages.success(request, 'Documento subido correctamente.')
            return redirect('documentos:lista')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/subir_documento.html', {'form': form, 'general': True})


@login_required
def subir_documento_caso(request, caso_id):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.causa_id = caso_id
            documento.save()
            log_action(request.user, 'SUBIR', 'Documento', documento.id, f'Subido documento a caso {caso_id}: {documento.titulo}')
            messages.success(request, 'Documento subido al caso correctamente.')
            return redirect('documentos:lista')
    else:
        form = DocumentoForm(initial={'causa': caso_id})
    return render(request, 'documentos/subir_documento.html', {'form': form, 'general': False, 'caso_id': caso_id})


def descargar_documento(request, token):
    notificacion = get_object_or_404(Notificacion, token=token)
    if notificacion.vigencia < timezone.now():
        raise Http404('Enlace expirado')
    documento = notificacion.documento
    file_path = documento.archivo.path
    if not os.path.exists(file_path):
        raise Http404('Archivo no encontrado')
    # Increment download counter
    notificacion.contador_descargas += 1
    notificacion.save()
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))


@login_required
def generar_notificacion(request, doc_id):
    """Create a Notificacion (temporary download link) for the given document."""
    documento = get_object_or_404(Documento, id=doc_id)
    # Create or get existing notificacion
    notificacion, created = Notificacion.objects.get_or_create(documento=documento)
    if created:
        log_action(request.user, 'COMPARTIR', 'Documento', documento.id, f'Generado enlace de descarga para: {documento.titulo}')
        messages.success(request, 'Enlace generado exitosamente.')
    else:
        messages.info(request, 'Ya existe un enlace activo para este documento.')
    return redirect('documentos:lista')
