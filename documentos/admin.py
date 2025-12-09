from django.contrib import admin
from .models import Documento, Notificacion

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'causa', 'folio', 'version', 'creado_en')
    list_filter = ('causa', 'creado_en')
    search_fields = ('titulo', 'archivo')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('documento', 'token', 'vigencia', 'contador_descargas')
    list_filter = ('vigencia',)
    readonly_fields = ('enlace',)
