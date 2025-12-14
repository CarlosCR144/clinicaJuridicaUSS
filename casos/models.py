from django.db import models
from django.conf import settings
from personas.models import Persona

class Tribunal(models.Model):
    nombre = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Causa(models.Model):
    ESTADOS = (
        ('en_estudio', 'En Estudio'),
        ('en_tramite', 'En Tramitación'),
        ('con_sentencia', 'Con Sentencia'),
        ('archivada', 'Archivada'),
    )

    rol_rit = models.CharField(max_length=50, verbose_name="RIT/Rol", unique=True)
    caratula = models.CharField(max_length=200)
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    cliente = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='causas')
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='casos_asignados')
    tribunal = models.ForeignKey(Tribunal, on_delete=models.SET_NULL, null=True)
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_estudio')
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.rol_rit} - {self.caratula}"

class Participante(models.Model):
    ROLES_CAUSA = (
        ('demandante', 'Demandante / Víctima'),
        ('demandado', 'Demandado / Imputado'),
        ('testigo', 'Testigo'),
        ('tercero', 'Tercero Interviniente'),
        ('abogado_contraparte', 'Abogado Contraparte'),
    )

    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='participantes')
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    rol = models.CharField(max_length=30, choices=ROLES_CAUSA)
    observaciones = models.TextField(blank=True)

    class Meta:
        # Evita duplicar a la misma persona con el mismo rol en la misma causa
        unique_together = ['causa', 'persona', 'rol'] 

    def __str__(self):
        return f"{self.persona} - {self.get_rol_display()}"

class Bitacora(models.Model):
    ACCIONES = (
        ('creacion', 'Creación de Expediente'),
        ('actualizacion', 'Actualización de Estado'),
        ('archivo', 'Subida de Documento'),
        ('agenda', 'Agendamiento de Cita'),
        ('nota', 'Nota Interna'),
    )

    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    detalle = models.TextField(blank=True, help_text="Descripción automática del cambio")

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_accion_display()} - {self.causa} ({self.fecha})"
    

# 
class RegistroCaso(models.Model):
    causa = models.OneToOneField('Causa', on_delete=models.CASCADE,related_name='registro')
    contenido = models.TextField(blank=True,default='')
    
    archivo = models.FileField(upload_to='expedientes/', blank=True, null=True, verbose_name="Expediente PDF")

    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True,blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Registro de {self.causa.rol_rit}"

class RegistroCasoHistorial(models.Model):
    causa = models.ForeignKey('Causa', on_delete=models.CASCADE,related_name='registro_historial')
    contenido = models.TextField() # snapshot del texto antes del cambip
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True,blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Historial de Registro de {self.causa.rol_rit} - {self.creado_en}"
    
