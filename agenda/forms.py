from django import forms
from .models import Cita
from casos.models import Participante
from django.utils import timezone

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['persona_atendida', 'tipo', 'fecha_hora', 'duracion', 'lugar', 'observaciones']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local',
            }),
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
        self.causa = kwargs.pop('causa', None)
        super().__init__(*args, **kwargs)

        if self.causa:
            ids_personas = list(Participante.objects.filter(causa=self.causa).values_list('persona_id', flat=True))
            ids_personas.append(self.causa.cliente.id)
            from personas.models import Persona
            self.fields['persona_atendida'].queryset = Persona.objects.filter(id__in=ids_personas)

    def clean_fecha_hora(self):
        fecha_ingresada = self.cleaned_data.get('fecha_hora')
        
        if fecha_ingresada:
            if fecha_ingresada < timezone.now():
                raise forms.ValidationError("No se pueden agendar citas en el pasado.")
        
        return fecha_ingresada