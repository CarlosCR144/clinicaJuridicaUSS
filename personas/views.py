# ejemplos MUY básicos, solo para probar que las urls funcionan

# personas/views.py
from django.shortcuts import render

def lista_usuarios(request):
    return render(request, 'personas/lista_usuarios.html', {'usuarios': []})

def crear_usuario(request):
    return render(request, 'personas/lista_usuarios.html')  # luego lo cambias a un form

def detalle_usuario(request, pk):
    return render(request, 'personas/detalle_usuario.html', {})  # luego agregas datos
