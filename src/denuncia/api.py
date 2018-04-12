#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import smart_str, smart_unicode
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone

from tastypie.resources import (
                        ModelResource,
                        ALL,
                        ALL_WITH_RELATIONS
                        )
from tastypie.authorization import Authorization
from tastypie import fields

from .models import Denuncia, Motivo
from institucion.models import Correo
from institucion.api import InstitucionResource
from localizaciones.api import (
    DepartamentoResource,
    MunicipioResource,
    DireccionResource
)

"""
Recurso de la api de motivos, mantiene al día los motivos por tipo.

Meta:
--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|   queryset       |     queryset    |  Lista de motivos para alimentar        |
|                  |                 |  al recurso.                            |
-------------------+-----------------+------------------------------------------
|  filtering       |   diccionario   |  Campos por los que se van a filtrar    |
|                  |                 |  los motivos. (por id, tipo             |
|                  |                 |  e institucion)                         |
-------------------+-----------------+------------------------------------------
|  allowed_methods |      lista      |  Metodos permitidos por la api,         |
|                  |                 |  en este caso solo permite GET.         |
-------------------+-----------------+------------------------------------------
|  resource_name   |      String     |  Nombre del recurso, se asigna a la URL.|
--------------------------------------------------------------------------------

No Meta:
--------------------------------------------------------------------------------
|   instituciones  |     FK     |  Relacion de este recurso con el recurso de  |
|                  |            |  las instituciones.                          |
--------------------------------------------------------------------------------
"""
class MotivoResource(ModelResource):

    instituciones = fields.ToManyField(
        InstitucionResource,
        attribute='instituciones',
        full=True,
        )

    class Meta:
        queryset = Motivo.objects.all()
        filtering = {
            'id': ALL,
            'tipo': ALL,
            'instituciones': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']
        resource_name = 'motivo'

"""
Recurso de las denuncias, solo sirve para recibir datos desde la aplicación
móvil.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|      motivo      |        FK       |  Relacion con el recurso de los motivos.|
-------------------+-----------------+------------------------------------------
|     direccion    |        FK       |  Relacion con el recurso de direccion.  |
-------------------+-----------------+------------------------------------------
|    obj_create    |      funcion    |  Al crear el objeto con los datos       |
|                  |                 |  ingresados con la api desde la aplica- |
|                  |                 |  ción móvil, se crea un objeto de tipo  |
|                  |                 |  EmailMultiAlternatives, para enviar el |
|                  |                 |  correo en html a la entidad correspon- |
|                  |                 |  diente. Retorna al objeto como tal.    |
--------------------------------------------------------------------------------

Meta:
--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|     queryset     |     queryset    |  Alimenta el recurso con denuncias.     |
-------------------+-----------------+------------------------------------------
|     filtering    |   diccionario   |  Campos por los que se van a filtrar    |
|                  |                 |  las denuncias. (por id, tipo, motivo y |
|                  |                 |  direccion)                             |
-------------------+-----------------+------------------------------------------
|  allowed_methods |      lista      |  Metodos permitidos por la api,         |
|                  |                 |  en este caso solo permite POST.        |
-------------------+-----------------+------------------------------------------
|  resource_name   |      String     |  Nombre del recurso, se asigna a la URL.|
-------------------+-----------------+------------------------------------------
|  authorization   |  Authorization  |  Autorizacion para postear contenido en |
|                  |                 |  las tablas de Denuncia.                |
--------------------------------------------------------------------------------
 """
class DenunciaResource(ModelResource):

    motivo = fields.ForeignKey(
        MotivoResource,
        attribute = 'motivo',
        full=True,
    )
    direccion = fields.ForeignKey(
        DireccionResource,
        attribute='direccion',
        full=True
    )

    def obj_create(self, bundle, **kwargs):

        #Obtiene el archivo.
        imgData = bundle.data.get('file')

        print bundle.data.get('latitud')
        print bundle.data.get('longitud')

        #Se verifica y se crea el objeto de su respectiva clase
        bundle.obj = self._meta.object_class()

        #Setea los atributos del objeto.
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        #Se "hidrata" del objeto y sus datos.
        bundle = self.full_hydrate(bundle)

        #Se guarda el objeto y se asigna en la variable objeto, se retorna.
        objeto = self.save(bundle)

        #El objeto ya fue guardado, solo se asigna la instancia a esta variable.
        denuncia = bundle.obj

        #variable para verificar la existencia de geolocalización
        geo = False

        #Verfica la existencia de geolocalización
        if denuncia.latitud != 0 and denuncia.longitud != 0:
            geo = True

        #Obtenemos ubicación de la denuncia.
        municipio = denuncia.direccion.municipio
        departamento = municipio.departamento

        #Verificamos el motivo y sus instituciones relacionadas.
        motivo = denuncia.motivo
        vIn = motivo.instituciones.all()

        #Se obtienen los correos de las instituciones, para sus
        #respectivas ubicaciones y tipos.
        correos = Correo.objects.none()
        for institucion in vIn:
            if institucion.tipo == "MU":
                temp = Correo.objects.filter(
                            institucion = institucion,
                            municipio = municipio
                            )
            else:
                temp = Correo.objects.filter(
                            institucion = institucion,
                            municipio__departamento = departamento
                            )
            correos = correos | temp

        try:
            text_content = 'Denuncia'

            #Se obtiene el template del correo.
            mail_html = get_template('correo.html')

            #Se renderiza el contexto y el template
            d = Context({
                    'motivo':motivo,
                    'denuncia': denuncia.denuncia,
                    'geo': geo,
                    'referencia': denuncia.referencia,
                    'latitud': denuncia.latitud,
                    'longitud': denuncia.longitud,
                    'label': motivo.motivo[0],
                    'fecha': timezone.localtime(denuncia.fecha).strftime('%d-%b-%Y %-I:%M %p %Z'),
                    'direccion': denuncia.direccion.direccion+", "+municipio.nombre+", "+departamento.nombre,
                    'tipo': motivo.tipo
                    })

            #Template renderizado.
            html_content = mail_html.render(d)

            #Información del correo.
            from_email = '"DenunciApp Guatemala" <denuncias@denunciappguatemala.com>'

            to = correos

            #Se crea el correo, parametros:
            #motivo, motivo del correo.
            #text_content, contenido para el correo en texto plano
            #from_email, quien envía el correo.
            #to, a donde se envía el correo. Tiene que ser una lista.
            msg = EmailMultiAlternatives(motivo, text_content, from_email, to)

            #Se adjunta el contenido en html.
            msg.attach_alternative(html_content, "text/html")

            #Extrae la imagen del archivo, obteniendo del base64, su tipo
            #y el codigo de la imagen.
            try:
                if len(imgData)>0:

                    quitar = ""

                    #Separa el codigo base64 de su MIME part.
                    quitar, imgData = imgData.split("data:", 1)
                    mime, imgData = imgData.split(";base64,")
                    quitar, tipo = mime.split('/')

                    #Se agrega una parte perdida para que el decoder la
                    #identifique como base64
                    missing_padding = 4 - len(imgData) % 4
                    if missing_padding:
                        imgData += b'='* missing_padding

                    #Se adjunta al mail:
                    #Nombre de la imagen, 'denuncia.' + tipo, tipo extraído del
                    #                      MIME part, se concatena como extensión
                    #                      del archivo.
                    #Archivo, imgData.decode('base64'), Para adjuntarlo, se
                    #                                   decodifica el base64.
                    #MIME, mime, tipo del archivo extraído del base64.
                    msg.attach('denuncia.' + tipo ,imgData.decode('base64'), mime)

            except Exception, ex:
                print ex, '1'

            msg.send()

        except Exception, ex:
            print ex, '2'

        #Retorna el objeto que se guardo al inicio.
        return objeto

    class Meta:
        queryset = Denuncia.objects.all()
        filtering = {
            'id': ALL,
            'tipo': ALL,
            'motivo': ALL_WITH_RELATIONS,
            'direccion': ALL_WITH_RELATIONS
        }
        allowed_methods = ['post']
        resource_name = 'denuncia'
        authorization = Authorization()
