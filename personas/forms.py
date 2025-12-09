from django import forms
from .models import Persona, Usuario

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['rut', 'nombres', 'apellidos', 'email', 'telefono', 'direccion']

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rut', 'telefono', 'rol', 'password']
        widgets = {
            'rol': forms.Select(choices=Usuario.ROL_CHOICES),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user
