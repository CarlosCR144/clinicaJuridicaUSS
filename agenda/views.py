from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from .models import Cita
from .forms import CitaForm

@login_required
def lista_citas(request):
    cita_list = Cita.objects.select_related('causa', 'responsable', 'persona_atendida').all().order_by('-fecha_hora')
    paginator = Paginator(cita_list, 10)  # Show 10 appointments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'agenda/lista_citas.html', {'citas': page_obj})

@login_required
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita creada exitosamente.')
            return redirect('agenda:lista')
    else:
        form = CitaForm()
    return render(request, 'agenda/form_cita.html', {'form': form, 'accion': 'Crear'})

@login_required
def detalle_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    return render(request, 'agenda/detalle_cita.html', {'cita': cita})

@login_required
def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada.')
            return redirect('agenda:detalle', pk=pk)
    else:
        form = CitaForm(instance=cita)
    return render(request, 'agenda/form_cita.html', {'form': form, 'accion': 'Editar'})

@login_required
def eliminar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada.')
        return redirect('agenda:lista')
    return render(request, 'agenda/eliminar_cita.html', {'cita': cita})
