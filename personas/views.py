# ejemplos MUY básicos, solo para probar que las urls funcionan

# personas/views.py
from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import PersonaForm, UsuarioForm
from .models import Persona, Usuario, AuditLog

from django.contrib.auth.decorators import login_required

@login_required
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'personas/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('personas:lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'personas/crear_usuario.html', {'form': form})

@login_required
def detalle_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'personas/detalle_usuario.html', {'usuario': usuario})

@login_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('personas:detalle_usuario', pk=pk)
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'personas/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado.')
        return redirect('personas:lista_usuarios')
    return render(request, 'personas/eliminar_usuario.html', {'usuario': usuario})

# Persona CRUD

@login_required
def lista_personas(request):
    personas = Persona.objects.all()
    return render(request, 'personas/lista_personas.html', {'personas': personas})

@login_required
def crear_persona(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona creada.')
            return redirect('personas:lista_personas')
    else:
        form = PersonaForm()
    return render(request, 'personas/crear_persona.html', {'form': form})

@login_required
def detalle_persona(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    return render(request, 'personas/detalle_persona.html', {'persona': persona})

@login_required
def editar_persona(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            messages.success(request, 'Persona actualizada.')
            return redirect('personas:detalle_persona', pk=pk)
    else:
        form = PersonaForm(instance=persona)
    return render(request, 'personas/editar_persona.html', {'form': form, 'persona': persona})

@login_required
def eliminar_persona(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    if request.method == 'POST':
        persona.delete()
        messages.success(request, 'Persona eliminada.')
        return redirect('personas:lista_personas')
    return render(request, 'personas/eliminar_persona.html', {'persona': persona})


@login_required
def audit_log(request):
    if not request.user.is_staff: # Only staff/admin should see logs
        messages.error(request, 'No tiene permisos para ver el registro de auditoría.')
        return redirect('home')
    logs = AuditLog.objects.select_related('usuario').all().order_by('-fecha')
    return render(request, 'personas/audit_log.html', {'logs': logs})
