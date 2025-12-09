from django.db import models
from django.db.models import Max
from datetime import timedelta
from django.utils import timezone


def default_vigencia():
    return timezone.now() + timedelta(days=7)
from django.conf import settings
import os
import uuid


def documento_upload_path(instance, filename):
    # Store files under media/documents/<causa_id>/
    return os.path.join('documents', str(instance.causa.id), filename)


class Documento(models.Model):
    causa = models.ForeignKey('casos.Causa', on_delete=models.CASCADE, related_name='documentos')
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to=documento_upload_path)
    folio = models.PositiveIntegerField(editable=False)
    version = models.PositiveIntegerField(default=1, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Assign folio: next integer for this causa
            last_folio = Documento.objects.filter(causa=self.causa).aggregate(models.Max('folio'))['folio__max']
            self.folio = (last_folio or 0) + 1
        else:
            # If same title exists for this causa, increment version
            if Documento.objects.filter(causa=self.causa, titulo=self.titulo).exclude(id=self.id).exists():
                self.version = Documento.objects.filter(causa=self.causa, titulo=self.titulo).aggregate(models.Max('version'))['version__max'] + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} (Folio {self.folio}, v{self.version})"


class Notificacion(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='notificaciones')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enlace = models.URLField(blank=True)
    vigencia = models.DateTimeField(default=default_vigencia)
    contador_descargas = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.enlace:
            self.enlace = f"/documentos/descargar/{self.token}/"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notificacion for {self.documento.titulo} (token {self.token})"

