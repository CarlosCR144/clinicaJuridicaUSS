from django.shortcuts import render

def calendario(request):
    return render(request, 'agenda/calendario.html')

def agendar_cita(request):
    return render(request, 'agenda/agendar_cita.html')
