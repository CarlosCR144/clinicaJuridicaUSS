from django.db import models
from django.conf import settings
from casos.models import Causa
import os
import hashlib

class Documento(models.Model):
    TIPOS_DOCUMENTO = (
        ('escrito', 'Escrito Judicial'),
        ('resolucion', 'Resolución / Sentencia'),
        ('oficio', 'Oficio'),
        ('prueba', 'Medio de Prueba'),
        ('informe', 'Informe Técnico'),
        ('otro', 'Otro'),
    )

    ESTADOS = (
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobado', 'Aprobado / Oficial'),
        ('rechazado', 'Rechazado / Corregir'),
    )

    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='documentos')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    nombre = models.CharField(max_length=255, verbose_name="Nombre / Carátula del Escrito")
    tipo = models.CharField(max_length=20, choices=TIPOS_DOCUMENTO, default='escrito')
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones_rechazo = models.TextField(blank=True, verbose_name="Motivo del rechazo")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='docs_aprobados'
    )

    folio = models.PositiveIntegerField(editable=False) 
    version = models.PositiveIntegerField(default=1, editable=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    hash_archivo = models.CharField(max_length=64, blank=True, null=True)
    hash_fallido = models.CharField(max_length=64, blank=True, null=True, editable=False)

    class Meta:
        ordering = ['causa', 'folio']
        unique_together = ('causa', 'folio')

    def __str__(self):
        return f"Folio {self.folio} - {self.nombre} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        # 1. Foliación Automática
        if not self.folio:
            ultimo_doc = Documento.objects.filter(causa=self.causa).order_by('-folio').first()
            self.folio = (ultimo_doc.folio + 1) if ultimo_doc else 1
        
        # 2. Hash SHA-256
        if self.archivo and not self.hash_archivo:
            sha256 = hashlib.sha256()
            for chunk in self.archivo.chunks():
                sha256.update(chunk)
            self.hash_archivo = sha256.hexdigest()

        # 3. Auto-aprobación si quien sube es Director o Supervisor
        if self.subido_por and self.subido_por.rol in ['director', 'supervisor']:
            if self.estado == 'pendiente':
                self.estado = 'aprobado'

        super().save(*args, **kwargs)
    
    def verificar_integridad(self):
        if not self.archivo or not self.hash_archivo:
            return True, None

        try:
            sha256 = hashlib.sha256()
            with open(self.archivo.path, 'rb') as f:
                for chunk in f:
                    sha256.update(chunk)
            
            hash_actual = sha256.hexdigest()
            
            # Comparamos
            es_valido = (hash_actual == self.hash_archivo)
            return es_valido, hash_actual
            
        except FileNotFoundError:
            return None, None # Archivo borrado
        except Exception:
            return False, None # Error lectura

    def delete(self, *args, **kwargs):
        if self.archivo:
            if os.path.isfile(self.archivo.path):
                os.remove(self.archivo.path)
        super().delete(*args, **kwargs)