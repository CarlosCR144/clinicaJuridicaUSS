from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Cita
from .forms import CitaForm
from casos.models import Causa, Bitacora

# Vista para el Calendario General
@login_required
def calendario(request):
    ahora = timezone.localtime(timezone.now())
    inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    
    citas = Cita.objects.filter(fecha_hora__gte=inicio_dia).order_by('fecha_hora')
    
    if request.user.rol == 'estudiante':
        citas = citas.filter(responsable=request.user)
    
    context = {
        'citas': citas,
        'fecha_actual': ahora
    }
    return render(request, 'agenda/calendario.html', context)

class AgendarCitaView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'agenda/agendar_cita.html'

    def dispatch(self, request, *args, **kwargs):
        # Capturamos la causa desde la URL
        self.causa = get_object_or_404(Causa, pk=self.kwargs['caso_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # Pasamos la causa al formulario para filtrar el select de personas
        kwargs = super().get_form_kwargs()
        kwargs['causa'] = self.causa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caso'] = self.causa
        return context

    def form_valid(self, form):
        # 1. Asignar datos automáticos
        cita = form.save(commit=False)
        cita.causa = self.causa
        cita.responsable = self.request.user # El usuario logueado es responsable
        cita.save()

        # 2. Registrar en Bitácora (Trazabilidad)
        Bitacora.objects.create(
            causa=self.causa,
            usuario=self.request.user,
            accion='agenda', # Asegúrate que 'agenda' esté en las choices de Bitacora
            detalle=f"Se agendó {cita.get_tipo_display()} para el {cita.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        )

        messages.success(self.request, "Cita agendada correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        # Volver al detalle del caso
        return reverse('casos:detalle', kwargs={'pk': self.causa.pk})