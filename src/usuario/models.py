# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser


"""
Gestor de usuarios personalizado. Crea usuarios bajo las necesidades de la app.
Hereda del gestor base de Django. (BaseUserManager)

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|    create_user   |      funcion    |  Retorna un objeto Usuario, un usuario  |
|                  |                 |  normal con privilegios limitados.      |
--------------------------------------------------------------------------------
| create_superuser |      funcion    |  También retorna un objero Usuario, pero|
|                  |                 |  con privilegios de superusuario,       |
|                  |                 |  utilizando el metodo 'create_user'.    |
--------------------------------------------------------------------------------
"""
class UsuarioManager(BaseUserManager):

    def create_user(self, username, correo, nombre, apellidos, password=None):

        #Si falta alguno de esos valores, o no es valido,
        #lanza un error de Valor.
        if not username:
            raise ValueError('Ingrese un nombre de usuario valido.')
        if not correo:
            raise ValueError('Ingrese una direccion de correo valida.')
        if not nombre:
            raise ValueError('Ingrese uno o mas nombres.')
        if not apellidos:
            raise ValueError('Ingrese sus apellidos.')

        #Se crea al usuario utilizando su modelo.
        usuario = self.model(
            username = username,
            correo = self.normalize_email(correo),
            nombre = nombre,
            apellidos = apellidos
        )

        #Se setea la contraseña, el metodo 'set_password' aplica el hash al
        #texto plano de la contraseña y lo guarda en el campo 'password' del
        #modelo usuario.
        usuario.set_password(password)
        #Se guarda el usuario en la tabla.
        usuario.save()

        return usuario

    def create_superuser(self, username, correo, nombre, apellidos, password=None):

        #Se crea al usuario normal.
        usuario = self.create_user(username, correo, nombre, apellidos, password)
        #Se le asignan los privilegios.
        usuario.is_admin = True
        usuario.is_staff = True
        usuario.is_active = True
        #Se guarda.
        usuario.save()

        return usuario


"""
Modelo que guarda a los usuarios, tiene como gestor a UsuarioManager, hereda de
AbstractBaseUser.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|        id        |       PK        |  Llave primaria de Usuario.             |
|                  |      (INT)      |                                         |
--------------------------------------------------------------------------------
|      nombre      |  CharField(55)  |  Nombre o nombres del usuario. Es       |
|                  |                 |  obligatorio.                           |
--------------------------------------------------------------------------------
|     apellidos    |  CharField(55)  |  Apellidos del usuario. Es obligatorio. |
--------------------------------------------------------------------------------
|     username     |  CharField(25)  |  Nombre de usuario. Es obligatorio.     |
--------------------------------------------------------------------------------
|      correo      |   EmailField    |  Correo del usuario. Es obligatorio y   |
|                  |                 |  unico.                                 |
--------------------------------------------------------------------------------
|  ultima_conexion |  DateTimeField  |  Informa cuando fue la ultima vez que el|
|                  |                 |  usuario se conecto al sistema.         |
--------------------------------------------------------------------------------
|     is_staff     |  BooleanField   |  Identifica al usuario como             |
|                  |                 |  superusuario.                          |
--------------------------------------------------------------------------------
|     is_admin     |  BooleanField   |  Identifica al usuario como usuario con |
|                  |                 |  con privilegios medios.                |
--------------------------------------------------------------------------------
|      is_res      |  BooleanField   |  Identifica al usuario como usuario de  |
|                  |                 |  privilegios bajos. Usuario promedio.   |
--------------------------------------------------------------------------------
|    is_active     |  BooleanField   |  Define si el usuario está activo.      |
--------------------------------------------------------------------------------
|    institucion   |       FK        |  Relacion con el modelo Institucion,    |
|                  |                 |  indica a que institucion pertenece el  |
|                  |                 |  usuario.                               |
--------------------------------------------------------------------------------
|       zona       |       FK        |  Relacion con el modelo Direccion,      |
|                  |                 |  indica la ubicacion del usuario.       |
--------------------------------------------------------------------------------
|      objects     |  UsuarioManager |  Indica que gestor de objetos utiliza   |
|                  |                 |  el modelo.                             |
--------------------------------------------------------------------------------
|  USERNAME_FIELD  |      String     |  Indica que campo de la clase se        |
|                  |                 |  utiliza como nombre de usuario.        |
--------------------------------------------------------------------------------
|  REQUIRED_FIELDS |      lista      |  Indica que campos son obligatorios.    |
--------------------------------------------------------------------------------
|   get_full_name  |     funcion     |  Retorna la concatenacion de 'nombre' y |
|                  |                 |  'apellidos' del usuario.               |
--------------------------------------------------------------------------------
|  get_short_name  |     funcion     |  Retorna el 'nombre' del usuario.       |
--------------------------------------------------------------------------------
|    __unicode__   |     funcion     |  Representación del obejto como una     |
|                  |                 |  cadena, en este caso, es el 'username'.|
--------------------------------------------------------------------------------
| has_module_perms |     funcion     |  Funcion que compara permisos del       |
|                  |                 |  usuario, en este modelo no se utiliza, |
|                  |                 |  siempre retorna verdadero.             |
--------------------------------------------------------------------------------
|    has_perm      |     funcion     |  Funcion que compara el permiso del     |
|                  |                 |  usuario, en este modelo no se utiliza, |
|                  |                 |  siempre retorna verdadero.             |
--------------------------------------------------------------------------------
"""
class Usuario(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=55)
    apellidos = models.CharField(max_length=55)
    username = models.CharField(max_length=25, unique=True)
    correo = models.EmailField(unique=True)
    ultima_conexion = models.DateTimeField(auto_now_add=True, auto_now=False)
    #Permisos a todo el sistema.
    is_staff = models.BooleanField(default=False)
    #Permisos al sistema de denuncias por departamento e institucion.
    #Se otorga a usuarios de analisis.
    is_admin = models.BooleanField(default=False)
    #Permisos al sistema de denuncias por departamento e institucion.
    #Solo de los ultimos 7 dias.
    #Se otorga a usuarios de respuesta.
    is_res = models.BooleanField(default=True)

    is_active = models.BooleanField(default=False)

    institucion = models.ForeignKey('institucion.Institucion', default = 1)
    zona = models.ForeignKey('localizaciones.Direccion', default = 1)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nombre', 'apellidos', 'correo']

    def get_full_name(self):
        return self.nombre + " " + self.apellidos

    def get_short_name(self):
        return self.nombre

    def __unicode__(self):
        return self.username

    def has_module_perms(self, perm_list):
        return True

    def has_perm(self, perm):
        return True
