# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Denuncia, Motivo


class DenunciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'motivo', 'tipo', 'denuncia','direccion','referencia', 'fecha']

class MotivoAdmin(admin.ModelAdmin):
    list_display = ['id', 'motivo' ,'cantidad', 'get_instituciones']

admin.site.register(Denuncia, DenunciaAdmin)
admin.site.register(Motivo, MotivoAdmin)
