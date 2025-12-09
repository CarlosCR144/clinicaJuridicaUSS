from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
    ROL_CHOICES = (
        ('director', 'Director/a de Clínica'),
        ('secretaria', 'Secretaría / Apoyo'),
        ('estudiante', 'Estudiante / Clínico'),
        ('supervisor', 'Abogado Supervisor'),
        ('admin', 'Administrador del Sistema'),
    )
    
    rut = models.CharField(max_length=12, unique=True, verbose_name='RUT')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='estudiante')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_rol_display()})"

class Persona(models.Model):
    rut = models.CharField(max_length=12, unique=True, verbose_name='RUT')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rut})"

class AuditLog(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=50)  # CREAR, EDITAR, ELIMINAR, SUBIR, DESCARGAR
    modelo = models.CharField(max_length=50)  # Causa, Documento, Persona, Cita
    registro_id = models.CharField(max_length=50) # ID del objeto afectado
    detalle = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} {self.modelo} - {self.fecha}"