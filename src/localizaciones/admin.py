from django.contrib import admin

from .models import Departamento,Municipio,Direccion

class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['id','codigo','nombre']

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id','nombre', 'departamento']

class DireccionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'direccion',
        'municipio',
#        'municipio.departamento'
        ]

admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Direccion, DireccionAdmin)
