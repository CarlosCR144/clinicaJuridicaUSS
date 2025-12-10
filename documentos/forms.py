from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'tipo', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Demanda inicial'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        # Validación básica de tamaño (ej: máx 10MB)
        if archivo:
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo es demasiado grande (Máx 10MB).")
        return archivo