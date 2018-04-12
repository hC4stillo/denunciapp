# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

"""
Modelo que contiene la lista de instituciones con las que trabaja el sistema.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|        id        |       PK        |  Llave primaria de Institucion.         |
|                  |      (INT)      |                                         |
--------------------------------------------------------------------------------
|   TIPO_CHOICES   |      Tupla      |  Contiene a los tipos de institucion    |
|                  |                 |  Se utilizan en la variable 'tipo'.     |
|                  |                 |  Utiliza como indices a las 5 variables |
|                  |                 |  anteriores a ella.                     |
--------------------------------------------------------------------------------
|      nombre      |    CharField    |  Nombre de la institucion.              |
--------------------------------------------------------------------------------
|       tipo       |   CharField(2)  |  Tipo de la institucion, solo se puede  |
|                  |                 |  llenar con algun indice de             |
|                  |                 |  TIPO_CHOICES.                          |
--------------------------------------------------------------------------------
|    __unicode__   |     funcion     |  Representación del obejto como una     |
|                  |                 |  cadena, en este caso, es el 'nombre'.  |
--------------------------------------------------------------------------------
"""
class Institucion(models.Model):
    CRIMINAL = 'CR'
    MUNICIPAL = 'MU'
    MEDIO_AMBIENTE = 'MA'
    DERECHOS_HUMANOS = 'DH'
    NINGUNO = 'NG'

    TIPO_CHOICES = (
        (CRIMINAL, 'Criminal'),
        (MUNICIPAL, 'Municipal'),
        (MEDIO_AMBIENTE, 'Medio Ambiente'),
        (DERECHOS_HUMANOS, 'Derechos Humanos'),
        (NINGUNO, 'Ninguno')
    )

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank = False)
    tipo = models.CharField(
                    max_length=2,
                    choices=TIPO_CHOICES,
                    default=CRIMINAL
                    )


    def __unicode__(self):
        return self.nombre

"""
Modelo que registra a los correos de las instituciones, por municipio o
departamento.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|        id        |       PK        |  Llave primaria de Correo.              |
|                  |      (INT)      |                                         |
--------------------------------------------------------------------------------
|      correo      |    EmailField   |  Correo correspondiente a una           |
|                  |                 |  institucion, especificamente a una     |
|                  |                 |  sucursal de un municipio o dep.        |
--------------------------------------------------------------------------------
|    institucion   |        FK       |  Relacion con el modelo Institucion,    |
|                  |                 |  indica a que institucion pertenece el  |
|                  |                 |  correo.                                |
--------------------------------------------------------------------------------
|     municipio    |        FK       |  Relacion con el modelo Municipio,      |
|                  |                 |  indica el municipio del correo, si la  |
|                  |                 |  institucion tiene una sucursal         |
|                  |                 |  departamental, se relaciona con la     |
|                  |                 |  cabecera.                              |
--------------------------------------------------------------------------------

"""
#concejomunixelaof@gmail.com
class Correo(models.Model):
    id = models.AutoField(primary_key=True)
    correo = models.EmailField()

    institucion = models.ForeignKey('Institucion')
    municipio = models.ForeignKey('localizaciones.Municipio')

    def __unicode__(self):
        return self.correo

    def get_departamento(self):
        return self.municipio.departamento

    class Meta:
        ordering = ['-municipio']
