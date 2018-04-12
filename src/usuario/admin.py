from django.contrib import admin

from .models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_full_name',
        'username',
        'correo',
        'ultima_conexion',
        'institucion',
        'zona'
        ]

# class TipoAdmin(admin.ModelAdmin):
#     list_display = ['id', 'tipo']

admin.site.register(Usuario, UsuarioAdmin)
# admin.site.register(Tipo_Usuario, TipoAdmin)
