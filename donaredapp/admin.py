from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Item, Categoria, Profile

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

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(Categoria)
