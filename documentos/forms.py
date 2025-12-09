from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['causa', 'titulo', 'archivo']
        widgets = {
            'causa': forms.HiddenInput(),
        }
