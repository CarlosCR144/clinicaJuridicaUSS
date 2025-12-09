from django import forms
from .models import Causa, Tribunal, Materia

class CausaForm(forms.ModelForm):
    class Meta:
        model = Causa
        fields = ['rol_rit', 'caratula', 'cliente', 'responsable', 'tribunal', 'materia', 'estado', 'descripcion']
        widgets = {
            'estado': forms.Select(choices=Causa.ESTADOS),
        }
