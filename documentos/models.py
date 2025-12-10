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

    causa = models.ForeignKey(Causa, on_delete=models.CASCADE, related_name='documentos')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # El archivo se guardará en: media/documentos/2025/10/nombre_archivo.pdf
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    
    nombre = models.CharField(max_length=255, verbose_name="Nombre / Carátula del Escrito")
    tipo = models.CharField(max_length=20, choices=TIPOS_DOCUMENTO, default='escrito')
    
    # Campos automáticos de control
    folio = models.PositiveIntegerField(editable=False) 
    version = models.PositiveIntegerField(default=1, editable=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    # Opcional: Hash para integridad
    hash_archivo = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ['causa', 'folio']
        # Aseguramos que el folio sea único por causa (no global)
        unique_together = ('causa', 'folio')

    def __str__(self):
        return f"Folio {self.folio} - {self.nombre} (v{self.version})"

    def save(self, *args, **kwargs):
        # 1. Lógica de Foliación Automática
        if not self.folio:
            ultimo_doc = Documento.objects.filter(causa=self.causa).order_by('-folio').first()
            self.folio = (ultimo_doc.folio + 1) if ultimo_doc else 1
        
        # 2. Lógica de Hash
        # Calculamos el hash solo si hay archivo y no tiene hash guardado (o si el archivo cambió)
        if self.archivo and not self.hash_archivo:
            sha256 = hashlib.sha256()
            for chunk in self.archivo.chunks():
                sha256.update(chunk)
            self.hash_archivo = sha256.hexdigest()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico cuando se borra el registro de BD
        if self.archivo:
            if os.path.isfile(self.archivo.path):
                os.remove(self.archivo.path)
        super().delete(*args, **kwargs)