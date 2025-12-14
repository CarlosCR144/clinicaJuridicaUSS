from django import forms
from .models import Causa, Participante, RegistroCaso
from django.contrib.auth import get_user_model

User = get_user_model()

class CausaForm(forms.ModelForm):
    class Meta:
        model = Causa
        fields = ['rol_rit', 'caratula', 'tribunal', 'materia', 'cliente', 'responsable', 'descripcion']
        widgets = {
            'rol_rit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: C-1234-2025'}),
            'caratula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez con González'}),
            'tribunal': forms.Select(attrs={'class': 'form-select'}),
            'materia': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SE PODRÍA AÑADIR DIRECTOR
        self.fields['responsable'].queryset = User.objects.filter(rol__in=['estudiante', 'supervisor'])
        self.fields['responsable'].label = "Procurador Responsable"
        self.fields['responsable'].required = False

    def clean_rol_rit(self):
        rit = self.cleaned_data['rol_rit'].upper().strip()
        return rit

class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['persona', 'rol', 'observaciones']
        widgets = {
            'persona': forms.Select(attrs={'class': 'form-select'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Opcional: Detalles adicionales...'}),
        }

    def __init__(self, *args, **kwargs):
        self.caso_id = kwargs.pop('caso_id', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        persona = cleaned_data.get('persona')
        rol = cleaned_data.get('rol')
        
        if self.caso_id and persona and rol:
            if Participante.objects.filter(causa_id=self.caso_id, persona=persona, rol=rol).exists():
                raise forms.ValidationError(f"{persona} ya está registrado como {rol} en este caso.")
        
        return cleaned_data
    
class RegistroCasoForm(forms.ModelForm):
    class Meta:
        model = RegistroCaso
        fields = ['contenido'] # solo se edita el texto
        widgets = {
                'contenido': forms.Textarea(attrs={
                'class':'form-control',
                'rows':10,
                'placeholder':'Escribe aquí el registro interno del caso...'
            })
        }

        labels = {
            'contenido': 'Registro interno del caso'
        }