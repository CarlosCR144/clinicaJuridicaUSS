from django.db import models
from django.conf import settings
from personas.models import Persona
from casos.models import Causa

class Cita(models.Model):
    TIPOS = (
        ('audiencia', 'Audiencia Judicial'),
        ('reunion_cliente', 'Reunión con Cliente'),
        ('interno', 'Coordinación Interna'),
    )
    
    ESTADOS = (
        ('programada', 'Programada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió'),
    )

    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='citas')
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    persona_atendida = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_hora = models.DateTimeField()
    duracion = models.PositiveIntegerField(default=60, help_text="Duración en minutos")
    tipo = models.CharField(max_length=20, choices=TIPOS, default='reunion_cliente')
    lugar = models.CharField(max_length=200, default="Oficinas Clínica Jurídica")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programada')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"