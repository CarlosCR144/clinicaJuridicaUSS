from django.shortcuts import render

def lista_casos(request):
    return render(request, 'casos/lista_casos.html')

def crear_caso(request):
    return render(request, 'casos/crear_caso.html')

def detalle_caso(request, pk):
    return render(request, 'casos/detalle_caso.html')
