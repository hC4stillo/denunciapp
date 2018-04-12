# -*- coding: utf-8 -*-

from django import forms

from .models import Denuncia, Motivo

# class CustomClearableFileInput(forms.ClearableFileInput):
#     template_with_clear = '<br>  <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label> %(clear)s'

class DenunciaForm(forms.ModelForm):

    class Meta:
        model = Denuncia

        fields = [
            'direccion',
            'referencia',
            'denuncia',
            'motivo',
            'tipo'
        ]

        # widgets = {
        #     'archivo': CustomClearableFileInput
        # }
