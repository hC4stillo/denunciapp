# -*- coding: utf-8 -*-

from django import forms
from django.core.mail import EmailMultiAlternatives

from .models import Usuario

class InicioForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class CambioPassForm(forms.Form):

    actual = forms.CharField(label='Password', widget=forms.PasswordInput())
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())

    def clean_password1(self):

        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")

        if password and password1 and password != password1:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        if password and password1 and len(password) < 8:
            raise forms.ValidationError("Ingrese una contraseña más larga.")

        return password1


class UserCreationForm(forms.ModelForm):

    # password = forms.CharField(label='Password', widget=forms.PasswordInput())
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput())

    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellidos',
            'username',
            'correo',
            'institucion',
            'zona'
        ]

    # def clean_password1(self):
    #
    #     password = self.cleaned_data.get("password")
    #     password1 = self.cleaned_data.get("password1")
    #
    #     if password and password1 and password != password1:
    #         raise forms.ValidationError("Las contraseñas no coinciden.")
    #     if password and password1 and len(password) < 8:
    #         raise forms.ValidationError("Ingrese una contraseña más larga.")
    #
    #     return password1

    def save(self, commit=True):

        usuario = super(UserCreationForm, self).save(commit=False)
        contrasena = Usuario.objects.make_random_password()

        text_content = 'Denuncia Movil: Contraseña y usuario.'
        html_content = '''<!DOCTYPE html><html><body><h1> Hola
                            ''' + str(self.cleaned_data.get("nombre"))+' '+str(self.cleaned_data.get("apellidos")) + '''</h1></br>
                            <h3> Este mensaje es para entregarte tu contraseña
                            y confirmar tu nombre de usuario.</h3><br>
                            <h4>Nombre de Usuario: ''' + str(self.cleaned_data.get("username")) + '''</h4></br>
                            <h4>Contraseña: ''' + str(contrasena) + '''</h4></br></body>
                            <footer><i>Los archivos quedan a cargo de la
                             entidad indicada.</i><br>
                            <i>Todos los datos de este correo son
                             confidenciales y no deben ser difundidos
                            a nadie más que las entidades interesadas
                             en ellos.</i></footer></html>'''

        from_email = '"Denuncia Movil" <denunciamovil@gmail.com>'
        msg = EmailMultiAlternatives(
            "Usuario y contraseña",
             text_content,
              from_email,
              [self.cleaned_data.get("correo")]
            )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        usuario.set_password(contrasena)

        if commit:
            usuario.save()

        return usuario
