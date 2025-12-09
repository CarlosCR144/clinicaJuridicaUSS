from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Causa
from .forms import CausaForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from agenda.models import Cita
from documentos.models import Documento
from personas.utils import log_action

@login_required
def home(request):
    # Statistics
    mis_casos_count = 0
    citas_hoy_count = 0
    docs_recent_count = 0
    
    if request.user.rol in ['estudiante', 'supervisor']:
        mis_casos_count = Causa.objects.filter(responsable=request.user).count()
        citas_hoy_count = Cita.objects.filter(responsable=request.user, fecha_hora__date=timezone.now().date()).count()
    else:
        # Admin/Director sees all
        mis_casos_count = Causa.objects.all().count()
        citas_hoy_count = Cita.objects.filter(fecha_hora__date=timezone.now().date()).count()
    
    docs_recent_count = Documento.objects.filter(creado_en__gte=timezone.now()-timezone.timedelta(days=7)).count()
    
    context = {
        'mis_casos_count': mis_casos_count,
        'citas_hoy_count': citas_hoy_count,
        'docs_recent_count': docs_recent_count,
    }
    return render(request, 'home.html', context)

@login_required
def lista_casos(request):
    casos = Causa.objects.select_related('cliente', 'responsable', 'tribunal', 'materia').all().order_by('-fecha_ingreso')
    return render(request, 'casos/lista_casos.html', {'casos': casos})

@login_required
def crear_caso(request):
    if request.method == 'POST':
        form = CausaForm(request.POST)
        if form.is_valid():
            caso = form.save()
            log_action(request.user, 'CREAR', 'Causa', caso.id, f'Creada causa: {caso.rol_rit}')
            messages.success(request, 'Causa creada exitosamente.')
            return redirect('casos:lista')
    else:
        form = CausaForm()
    return render(request, 'casos/crear_caso.html', {'form': form})

@login_required
def detalle_caso(request, pk):
    caso = get_object_or_404(Causa, pk=pk)
    return render(request, 'casos/detalle_caso.html', {'caso': caso})

@login_required
def editar_caso(request, pk):
    caso = get_object_or_404(Causa, pk=pk)
    if request.method == 'POST':
        form = CausaForm(request.POST, instance=caso)
        if form.is_valid():
            form.save()
            log_action(request.user, 'EDITAR', 'Causa', caso.id, f'Editada causa: {caso.rol_rit}')
            messages.success(request, 'Causa actualizada.')
            return redirect('casos:detalle', pk=pk)
    else:
        form = CausaForm(instance=caso)
    return render(request, 'casos/editar_caso.html', {'form': form, 'caso': caso})

@login_required
def eliminar_caso(request, pk):
    caso = get_object_or_404(Causa, pk=pk)
    if request.method == 'POST':
        identifier = f"{caso.rol_rit} - {caso.caratula}"
        caso.delete()
        log_action(request.user, 'ELIMINAR', 'Causa', pk, f'Eliminada causa: {identifier}')
        messages.success(request, 'Causa eliminada.')
        return redirect('casos:lista')
    return render(request, 'casos/eliminar_caso.html', {'caso': caso})

@login_required
def buscar_casos(request):
    query = request.GET.get('q', '')
    materia = request.GET.get('materia', '')
    casos_qs = Causa.objects.select_related('cliente', 'responsable', 'tribunal', 'materia')
    if query:
        casos_qs = casos_qs.filter(Q(caratula__icontains=query) | Q(descripcion__icontains=query))
    if materia:
        casos_qs = casos_qs.filter(materia__nombre__icontains=materia)
    paginator = Paginator(casos_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'casos/buscar_casos.html', {'page_obj': page_obj, 'query': query, 'materia': materia})
