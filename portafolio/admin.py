from django.contrib import admin
from django.utils.html import format_html
from .models import Comment, Client, Project

# Registro personalizado para Project
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'mostrar_imagen')
    search_fields = ('nombre', 'empresa')
    list_filter = ('empresa',)
    
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.imagen.url)
        return "Sin imagen"
    
    mostrar_imagen.short_description = 'Imagen'

# Registro de los demás modelos
admin.site.register(Client)
admin.site.register(Comment)