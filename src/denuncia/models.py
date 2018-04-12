# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db import models
from django.utils.encoding import smart_str, smart_unicode
from django.utils import timezone
from django.utils.encoding import smart_str, smart_unicode

"""
Tabla de la BD para guardar las denuncias.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|   TIPO_CHOICES   |      Tupla      |  Contiene a los tipos de denuncia que se|
|                  |                 |  pueden escoger. Se utilizan en la      |
|                  |                 |  variable 'tipo'. Utiliza como indices  |
|                  |                 |  a las 4 variables anteriores a ella.   |
--------------------------------------------------------------------------------
|        id        |       PK        |  Llave primaria de Denuncia.            |
|                  |      (INT)      |                                         |
--------------------------------------------------------------------------------
|      latitud     |    FloatField   |  Localizacion exacta de la denuncia.    |
--------------------------------------------------------------------------------
|     longitud     |    FloatField   |  Localizacion exacta de la denuncia.    |
--------------------------------------------------------------------------------
|     denuncia     |    TextField    |  Descripcion de la denuncia, puede      |
|                  |                 |  quedar en blanco.                      |
--------------------------------------------------------------------------------
|    referencia    |    CharField    |  Contiene un punto de referencia a la   |
|                  |                 |  ubucación de la denuncia.              |
--------------------------------------------------------------------------------
|      fecha       |  DateTimeField  |  Fecha y hora de la denuncia.           |
--------------------------------------------------------------------------------
|      tipo        |    CharField    |  Tipo de la denuncia, solo se puede     |
|                  |                 |  llenar con algún indice de             |
|                  |                 |  'TIPO_CHOICES'.                        |
--------------------------------------------------------------------------------
|      motivo      |       FK        |  Instancia y relación con el modelo     |
|                  |                 |  'Motivo'.                              |
--------------------------------------------------------------------------------
|     direccion    |       FK        |  Instancia y Relacion con el modelo     |
|                  |                 |  'Direccion', de la app localizaciones. |
--------------------------------------------------------------------------------
|    __unicode__   |     funcion     |  Representación del obejto como una     |
|                  |                 |  cadena, en este caso, es la 'denuncia'.|
--------------------------------------------------------------------------------
|     getSprite    |     funcion     |  Devuelve un entero con el valor de     |
|                  |                 |  la funcion 'sprite' del modelo 'motivo'|
|                  |                 |  para cortar la imagen de los marcadores|
|                  |                 |  que se muestran en el mapa.            |
--------------------------------------------------------------------------------
"""
class Denuncia(models.Model):

    CRIMINAL = 'CR'
    MUNICIPAL = 'MU'
    MEDIO_AMBIENTE = 'MA'
    DERECHOS_HUMANOS = 'DH'

    TIPO_CHOICES = (
        (CRIMINAL, 'Criminal'),
        (MUNICIPAL, 'Municipal'),
        (MEDIO_AMBIENTE, 'Medio Ambiente'),
        (DERECHOS_HUMANOS, 'Derechos Humanos'),
    )

    id = models.AutoField(primary_key=True)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    denuncia = models.TextField(blank=True)
    referencia = models.CharField(blank=True, max_length=140, default="")
    fecha = models.DateTimeField(auto_now=True, auto_now_add=False, blank = False)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default=CRIMINAL)

    motivo = models.ForeignKey('Motivo')
    direccion = models.ForeignKey('localizaciones.Direccion')

    verbose_name = 'Denuncias'

    def __unicode__(self):
        return self.denuncia

    def getSprite(self):
        return self.motivo.sprite()

#Cuando se borra una denuncia, al motivo se le resta uno en cantidad
@receiver(post_delete, sender=Denuncia)
def denuncia_delete(sender, instance, **kwargs):
    instance.motivo.cantidad -= 1
    instance.motivo.save()

#Cuando se inserta una denuncia, al motivo se le suma uno en cantidad
@receiver(post_save, sender=Denuncia)
def denuncia_save(sender, instance, **kwargs):
    instance.motivo.cantidad += 1
    instance.motivo.save()

"""
Tabla de la BD que contiene los motivos que se pueden asociar a las denuncias.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|   TIPO_CHOICES   |      Tupla      |  Contiene a los tipos del motivo que se |
|                  |                 |  pueden escoger. Se utilizan en la      |
|                  |                 |  variable 'tipo'. Utiliza como indices  |
|                  |                 |  a las 4 variables anteriores a ella.   |
--------------------------------------------------------------------------------
|        id        |       PK        |  Llave primaria de Motivo.              |
|                  |      (INT)      |                                         |
--------------------------------------------------------------------------------
|      motivo      |    CharField    |  Motivo por el cual se puede denunciar  |
--------------------------------------------------------------------------------
|     cantidad     |   IntegerField  | Cantidad de denuncias por este motivo.  |
--------------------------------------------------------------------------------
|      tipo        |    CharField    |  Tipo del motivo, solo se puede llenar  |
|                  |                 |  con algún indice de 'TIPO_CHOICES'.    |
--------------------------------------------------------------------------------
|   instituciones  | ManyToManyField |  Relacion muchos a muchos con el modelo |
|                  |                 |  Institucion de la app institucion.     |
--------------------------------------------------------------------------------
|    __unicode__   |     funcion     |  Representación del obejto como una     |
|                  |                 |  cadena, en este caso, es el 'motivo'.  |
--------------------------------------------------------------------------------
|    motivo_hash   |     funcion     |  Retorna el 'motivo' en formato hash md5|
|                  |                 |  para poder usarlo como nombre de       |
|                  |                 |  variable en JS al renderizar el        |
|                  |                 |  template de estadisticas.              |
--------------------------------------------------------------------------------
|     sumTotal     |     funcion     |  Cantidad de denuncias por este motivo. |
--------------------------------------------------------------------------------
| get_instituciones|     funcion     |  Retorna una concatenanacion de los     |
|                  |                 |  nombres de las instituciones           |
|                  |                 |  relacionadas al motivo.                |
--------------------------------------------------------------------------------
|      sprite      |     funcion     |  Retorna un entero, resultado de una    |
|                  |                 |  operación con el id, con el fin de     |
|                  |                 |  encontrar la posición del marcador     |
|                  |                 |  correspondiente al motivo en la imagen |
|                  |                 |  '/static/images/marcadores.png'        |
--------------------------------------------------------------------------------

Meta:
--------------------------------------------------------------------------------
|   verbose_name   |      String     |  Plural del nombre del modelo.          |
--------------------------------------------------------------------------------
|     ordering     |      array      |  Lista que indica por que parametros    |
|                  |                 |  se ordena la tabla del modelo. Se      |
|                  |                 |  ordena por cantidad.                   |
--------------------------------------------------------------------------------
"""
class Motivo(models.Model):
    CRIMINAL = 'CR'
    MUNICIPAL = 'MU'
    MEDIO_AMBIENTE = 'MA'
    DERECHOS_HUMANOS = 'DH'

    TIPO_CHOICES = (
        (CRIMINAL, 'Criminal'),
        (MUNICIPAL, 'Municipal'),
        (MEDIO_AMBIENTE, 'Medio Ambiente'),
        (DERECHOS_HUMANOS, 'Derechos Humanos'),
    )

    id = models.AutoField(primary_key=True)
    motivo = models.CharField(max_length=100)
    cantidad = models.IntegerField(default=0)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default=CRIMINAL)

    # correos = models.ManyToManyField('institucion.Correo')
    instituciones = models.ManyToManyField('institucion.Institucion')

    def __unicode__(self):
        splt = self.motivo.split('_')

        tmp = splt[0]
        i = 1
        while i<len(splt):
            tmp = tmp + ' ' + splt[i]
            i += 1
        return tmp

    def motivo_hash(self):
        return "h"+hashlib.md5(smart_str(self.motivo)).hexdigest()

    def sumTotal(self):
        denuncias = Denuncia.objects.filter(motivo=self)

        return len(denuncias)

    def get_instituciones(self):
        return ", ".join([m.nombre for m in self.instituciones.all()])

    def sprite(self):
        return self.id * 36

    class Meta:
        verbose_name = 'Motivos'
        ordering =['-cantidad']
