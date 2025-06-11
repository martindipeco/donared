from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import Item, Categoria, Profile, Solicitud, Resena

# Define an inline admin descriptor for the Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['movil', 'validado']  # Fields to display
    extra = 0  # Prevents extra empty forms from showing

# Extend the UserAdmin to include the Profile inline
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_validado']  # Add is_validado to list display

    def is_validado(self, obj):
        return obj.profile.validado if hasattr(obj, 'profile') else False
    is_validado.boolean = True  # Displays as a green check or red cross
    is_validado.short_description = 'Validado'  # Column header

class ItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'domicilio', 'latitude', 'longitude', 'fecha_creacion', 'activo')
    list_filter = ('categoria', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'domicilio')
    readonly_fields = ('fecha_creacion',)


class SolicitudAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = [
        'id',
        'item',
        'donante',
        'beneficiario', 
        'estado',
        'fecha_creacion'
    ]
    
    # Add filters in the right sidebar
    list_filter = [
        'estado',
        'fecha_creacion',
        'item__categoria',  # Assuming your Item model has a categoria field
    ]
    
    # Add search functionality
    search_fields = [
        'item__nombre',  # Assuming your Item model has a nombre field
        'donante__username',
        'donante__email',
        'beneficiario__username',
        'beneficiario__email',
    ]
    
    # Default ordering (newest first)
    ordering = ['-fecha_creacion']
    
    # Fields to display in the detail view
    fields = [
        'item',
        'donante',
        'beneficiario',
        'estado',
        'fecha_creacion',
    ]
    
    # Make fecha_creacion read-only since it's auto-generated
    readonly_fields = ['fecha_creacion']
    
    # Add actions for bulk operations
    actions = ['marcar_como_aceptada', 'marcar_como_rechazada', 'marcar_como_concretada']
    
    def marcar_como_aceptada(self, request, queryset):
        queryset.update(estado='ACEPTADA')
        self.message_user(request, f"{queryset.count()} solicitudes marcadas como aceptadas.")
    marcar_como_aceptada.short_description = "Marcar como aceptada"
    
    def marcar_como_rechazada(self, request, queryset):
        queryset.update(estado='RECHAZADA')
        self.message_user(request, f"{queryset.count()} solicitudes marcadas como rechazadas.")
    marcar_como_rechazada.short_description = "Marcar como rechazada"
    
    def marcar_como_concretada(self, request, queryset):
        queryset.update(estado='CONCRETADA')
        self.message_user(request, f"{queryset.count()} solicitudes marcadas como concretadas.")
    marcar_como_concretada.short_description = "Marcar como concretada"

class ResenaAdmin(admin.ModelAdmin):
    list_display = ['id', 'solicitud', 'calificacion', 'fecha_creacion', 'display_estado']
    list_filter = ['calificacion', 'fecha_creacion', 'estado']
    search_fields = ['solicitud__beneficiario__username', 'solicitud__donante__username', 'comentario']
    readonly_fields = ['fecha_creacion']
    actions = ['aprobar_seleccionadas', 'rechazar_seleccionadas']

    def display_estado(self, obj):
        color = 'black'
        if obj.estado == 'pending':
            color = 'orange'
        elif obj.estado == 'approved':
            color = 'green'
        elif obj.estado == 'rejected':
            color = 'red'

        if obj.estado == 'pending':
            return format_html('<a href="{}" style="color: {}; font-weight: bold;">{}</a>', obj.id, color, obj.get_estado_display())
        else:
            return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_estado_display())
    display_estado.short_description = 'Estado'

    def aprobar_seleccionadas(self, request, queryset):
        queryset.update(estado='approved')
        self.message_user(request, f"{queryset.count()} reseñas aprobadas correctamente.")
    aprobar_seleccionadas.short_description = "Aprobar reseñas seleccionadas"

    def rechazar_seleccionadas(self, request, queryset):
        queryset.update(estado='rejected')
        self.message_user(request, f"{queryset.count()} reseñas rechazadas correctamente.")
    rechazar_seleccionadas.short_description = "Rechazar reseñas seleccionadas"

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(Categoria)
admin.site.register(Solicitud, SolicitudAdmin)
admin.site.register(Resena, ResenaAdmin)