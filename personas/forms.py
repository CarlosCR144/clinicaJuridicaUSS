from django import forms
from django.core.exceptions import ValidationError
from .models import Persona, Usuario
from django.contrib.auth.forms import PasswordChangeForm
from .validators import validar_rut_chileno
import re
from django.contrib.auth import get_user_model

class PersonaForm(forms.ModelForm):
    rut = forms.CharField(
        validators=[validar_rut_chileno],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9', 'id': 'inputRut'})
    )
    
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'})
    )

    class Meta:
        model = Persona
        fields = ['rut', 'nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_rut(self):
        # Guarda el RUT siempre con formato: XX.XXX.XXX-Y
        rut = self.cleaned_data['rut'].upper().replace(".", "").replace("-", "")
        cuerpo = rut[:-1]
        dv = rut[-1]
        
        # Formatear con puntos
        cuerpo_fmt = "{:,}".format(int(cuerpo)).replace(",", ".")
        return f"{cuerpo_fmt}-{dv}"

    def clean_nombres(self):
        return self.cleaned_data['nombres'].title()

    def clean_apellidos(self):
        return self.cleaned_data['apellidos'].title()

    def clean_telefono(self):
        """
        Valida, limpia y estandariza el número de celular chileno.
        Entrada aceptada: 912345678, +56912345678, 9 1234 5678
        Salida estandarizada: +56 9 XXXX XXXX
        """
        telefono_raw = self.cleaned_data.get('telefono', '')
        
        if not telefono_raw:
            return ""

        # 1. Limpieza: Dejar solo dígitos
        solo_numeros = re.sub(r'\D', '', str(telefono_raw))
        
        cuerpo_celular = ""

        # 2. Lógica de detección (Prefijo 56 o directo)
        if len(solo_numeros) == 11 and solo_numeros.startswith("56"):
            cuerpo_celular = solo_numeros[2:] # Quitamos el 56
        elif len(solo_numeros) == 9:
            cuerpo_celular = solo_numeros
        else:
            raise ValidationError("El teléfono debe tener 9 dígitos válidos (Ej: 9 8765 4321).")

        # 3. Validar que sea móvil (empieza con 9)
        if not cuerpo_celular.startswith("9"):
            raise ValidationError("El número debe comenzar con 9 (formato móvil Chile).")

        # 4. Estandarización final para guardar en BD
        # Formato visual: +56 9 1234 5678
        telefono_formateado = f"+56 {cuerpo_celular[0]} {cuerpo_celular[1:5]} {cuerpo_celular[5:]}"
        
        return telefono_formateado

Usuario = get_user_model()

class UsuarioForm(forms.ModelForm):
    # 1. Validaciones robustas añadidas al Usuario
    rut = forms.CharField(
        validators=[validar_rut_chileno],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9', 'id': 'inputRutUser'})
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Requerido para nuevos usuarios. Deja vacío para mantener la actual si editas."
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Usuario
        # Agregamos 'telefono' que faltaba
        fields = ['username', 'first_name', 'last_name', 'email', 'rut', 'telefono', 'rol'] 
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # 'rut' se define arriba con el widget custom
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    # Reutilizamos lógica de limpieza
    def clean_rut(self):
        rut = self.cleaned_data['rut'].upper().replace(".", "").replace("-", "")
        cuerpo = rut[:-1]
        dv = rut[-1]
        cuerpo_fmt = "{:,}".format(int(cuerpo)).replace(",", ".")
        return f"{cuerpo_fmt}-{dv}"

    def clean_telefono(self):
        telefono_raw = self.cleaned_data.get('telefono', '')
        if not telefono_raw:
            return ""
        solo_numeros = re.sub(r'\D', '', str(telefono_raw))
        cuerpo_celular = ""
        if len(solo_numeros) == 11 and solo_numeros.startswith("56"):
            cuerpo_celular = solo_numeros[2:] 
        elif len(solo_numeros) == 9:
            cuerpo_celular = solo_numeros
        else:
            raise ValidationError("El teléfono debe tener 9 dígitos válidos (Ej: 9 8765 4321).")
        if not cuerpo_celular.startswith("9"):
            raise ValidationError("El número debe comenzar con 9 (formato móvil Chile).")
        return f"+56 {cuerpo_celular[0]} {cuerpo_celular[1:5]} {cuerpo_celular[5:]}"

    def clean_first_name(self):
        return self.cleaned_data['first_name'].title()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].title()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")

        if not self.instance.pk and not password:
            self.add_error('password', "La contraseña es obligatoria para nuevos usuarios.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    

class PasswordChangeFormBootstrap(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].label = "Contraseña actual"
        self.fields['new_password1'].label = "Nueva contraseña"
        self.fields['new_password2'].label = "Confirmar nueva contraseña"

        self.fields['new_password1'].help_text = (
            "<ul class='mb-0'>"
            "<li>Mínimo 8 caracteres</li>"
            "<li>No debe parecerse a tus datos personales</li>"
            "<li>No puede ser una contraseña común</li>"
            "<li>No puede ser solo números</li>"
            "</ul>"
        )

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})