from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['causa', 'responsable', 'persona_atendida', 'fecha_hora', 'duracion', 'tipo', 'lugar', 'estado', 'observaciones']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
