from django.contrib import admin

from .models import Institucion,Correo

class CorreoAdmin(admin.ModelAdmin):
    list_display = [
            'correo',
            'institucion',
            'municipio',
            'get_departamento'
            ]

admin.site.register(Institucion)
# admin.site.register(Sede)
# admin.site.register(Telefono)
admin.site.register(Correo, CorreoAdmin)
