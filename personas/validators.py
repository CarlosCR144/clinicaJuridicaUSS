from django.core.exceptions import ValidationError
import re

def validar_rut_chileno(value):
    """
    Valida que el RUT sea técnicamente válido (Módulo 11).
    Acepta formatos con o sin puntos y con guion.
    """
    rut = value.upper().replace("-", "").replace(".", "")
    
    if not rut:
        raise ValidationError("El RUT no puede estar vacío.")
        
    if len(rut) < 7:
        raise ValidationError("El RUT es demasiado corto.")

    aux = rut[:-1] # Cuerpo del RUT
    dv = rut[-1:]  # Dígito Verificador

    if not aux.isdigit():
         raise ValidationError("El cuerpo del RUT debe contener solo números.")

    revertido = map(int, reversed(str(aux)))
    factors = [2, 3, 4, 5, 6, 7]
    s = sum(d * factors[i % 6] for i, d in enumerate(revertido))
    res = 11 - (s % 11)

    if res == 11:
        dv_esperado = '0'
    elif res == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(res)

    if dv != dv_esperado:
        raise ValidationError("El RUT ingresado no es válido.")

def solo_numeros(value):
    """Valida que el campo contenga solo dígitos y opcionalmente el símbolo +"""
    if not re.match(r'^\+?\d+$', value):
        raise ValidationError("Este campo solo debe contener números.")