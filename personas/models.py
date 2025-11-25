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