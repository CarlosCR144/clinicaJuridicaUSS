from django import forms
from .models import Cita
from casos.models import Participante

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['persona_atendida', 'tipo', 'fecha_hora', 'duracion', 'lugar', 'observaciones']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos (ej: 60)'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sala 1, Zoom, Juzgado...'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'persona_atendida': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'persona_atendida': 'Con quién (Opcional)',
            'fecha_hora': 'Fecha y Hora',
        }

    def __init__(self, *args, **kwargs):
        # Recibimos el objeto 'causa' para filtrar personas
        self.causa = kwargs.pop('causa', None)
        super().__init__(*args, **kwargs)

        if self.causa:
            # Lógica para mostrar solo gente del caso
            # 1. Obtenemos IDs de los participantes extras
            ids_personas = list(Participante.objects.filter(causa=self.causa).values_list('persona_id', flat=True))
            # 2. Agregamos al cliente principal
            ids_personas.append(self.causa.cliente.id)
            
            # 3. Filtramos el QuerySet del campo
            from personas.models import Persona
            self.fields['persona_atendida'].queryset = Persona.objects.filter(id__in=ids_personas)