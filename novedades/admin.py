from django.contrib import admin
from .models import Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha_publicacion', 'estado')
    list_filter = ('estado', 'fecha_publicacion', 'autor')
    search_fields = ('titulo', 'descripcion')
    date_hierarchy = 'fecha_publicacion'
    ordering = ('-fecha_publicacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('titulo', 'descripcion', 'imagen')
        }),
        ('Metadatos', {
            'fields': ('autor', 'estado', 'fecha_publicacion')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
