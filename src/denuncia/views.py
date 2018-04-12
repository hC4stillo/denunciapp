# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta

from django.shortcuts import render, redirect
from django.utils.encoding import smart_str, smart_unicode
from django.core.mail import send_mail
from django.core.serializers.json import Serializer
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core import mail
from django.core import serializers
from django.core.mail import EmailMessage
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.template import Context
from django.template.loader import get_template

from .forms import DenunciaForm
from institucion.models import Correo, Institucion
from localizaciones.models import Departamento, Municipio, Direccion
from .models import Motivo, Denuncia

#------------------------------------------------
"""
Serializador JSON para el modelo Denuncia, hereda de json.Serializer.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|  get_dump_object |     funcion     |  Actualiza el diccionario que será      |
|                  |                 |  serializado, agregando más información |
|                  |                 |  sirve para llenar el mapa de la app.   |
--------------------------------------------------------------------------------
"""
class DenunciaSerializer(Serializer):

    def get_dump_object(self, obj):
        #Se obtiene la fecha del objeto y se formatea a la zona local.
        fecha = timezone.localtime(obj.fecha)

        dic = {
            #Se obtiene la posicion del marcador del motivo.
            "sprite": obj.getSprite(),
            #Motivo de la denuncia.
            "motivo": obj.motivo.motivo,
            #La fecha se formatea como ej: "1-Dec-2016 3:00 PM CST"
            "fecha": fecha.strftime('%d-%b-%Y %-I:%M %p %Z'),
            #Coordenadas de la denuncia.
            "latitud": obj.latitud,
            "longitud": obj.longitud,
        }

        return dic


"""
Retorna una respuesta en JSON, que es consumida por Ajax desde la applicacion
móvil. La respuesta tiene información de la ubicación de las denuncias, con esto
se llena el mapa de denuncias. Se devuelven solo las denuncias hechas en los
últimos siete días.
"""
def getDenuncias(request):

    #Se filtran las denuncias que no tienen ubicación.
    denuncias = Denuncia.objects.exclude(longitud = 0, latitud = 0)
    denuncias = denuncias.exclude(longitud = None, latitud = None)

    #Se filtran las denuncias con más de siete días de antigüedad.
    fecha_desde = timezone.now()-timedelta(days=7)
    denuncias = denuncias.filter(
        fecha__range = (
            fecha_desde,
            timezone.now()
        )
    )

    #Se serializan las denuncias con el serializador personalizado.
    data = DenunciaSerializer().serialize(denuncias)

    return HttpResponse(data, content_type='application/json')

#------------------------------------------------

"""
Vista para realizar denuncias, funciona de la misma forma que la api.
"""
def denunciar(request):

    instituciones = Institucion.objects.all()
    departamentos = Departamento.objects.all()
    if request.method == 'POST':
        form = DenunciaForm(request.POST or None, request.FILES or None)
        Post = True

        if form.is_valid():
            clean = form.cleaned_data

            is_valid = True

            denuncia = Denuncia()

            denuncia.direccion = clean['direccion']
            denuncia.referencia = clean['referencia']
            denuncia.denuncia = clean['denuncia']
            denuncia.latitud = request.POST['lat']
            denuncia.longitud = request.POST['lon']

            geo = False

            if denuncia.latitud != 0 and denuncia.longitud != 0:
                geo = True

            if request.FILES:
                archivo = request.FILES['file']

            denuncia.motivo = clean['motivo']

            denuncia.save()

            municipio = denuncia.direccion.municipio
            departamento = municipio.departamento

            motivo = denuncia.motivo
            vIn = motivo.instituciones.all()

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

            #Envio de correo----------------------------------------------------

            text_content = 'Denuncia'

            mail_html = get_template('correo.html')

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

            html_content = mail_html.render(d)

            from_email = '"DenunciApp Guatemala" <denuncias@denunciappguatemala.com>'

            to = correos
            msg = EmailMultiAlternatives(motivo, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            if request.FILES:
                msg.attach(archivo.name,archivo.read(),archivo.content_type)
            msg.send()

            #Cierre de conexion-------------------------------------------------

            return redirect('success')

        else:
            messages.error(request, 'Ingresa correctamente los datos.')

    else:
        form = DenunciaForm()
        Post = False
        is_valid = False

    context = {
        'form':form,
        # 'instituciones': instituciones,
        'departamentos': departamentos,
        }

    return render(request,'denuncia.html',context)

"""
Muestra un mensaje de exito.
"""
def success(request):
    return render(request,'success.html',{})

"""
Retorna una respuesta JSON con una lista de motivos filtrados por tipo.
Si se especifica otro parametro en la URL, se busca por institucion.
"""
def busquedaMo(request):
    vID = request.GET['id']

    try:
        #Si existe el parametro 'tipo' en la URL, se buscan los motivos
        #filtrados por institucion.
        if request.GET['tipo']:
            mots = Motivo.objects.filter(instituciones__id=vID)

    except:
        #Si no, solo se filtran por tipo.
        mots = Motivo.objects.filter(tipo = vID)

    data = serializers.serialize('json', mots, fields = ('motivo'))

    return HttpResponse(data, content_type='application/json')

"""
Vista que muestra la lista de denuncias, dependiendo de los privilegios del
usuario.
"""
@login_required(login_url='inicio')
def denunciasList(request):
    #Se obtiene la informacion del usuario.
    zona = request.user.zona
    tipo = request.user.institucion.tipo
    institucion = request.user.institucion

    #En la vista, se utiliza la lista de motivos para hacer busquedas.
    motivos = Motivo.objects.all()

    #Si es superusuario, se le da acceso completo, las denuncias se ordenan por
    #fecha, desde la más reciente.
    if request.user.is_staff:
        denuncias = Denuncia.objects.all().order_by('-fecha')
    #Si no, Se verifica que tipo es.
    else:
        #Si no tiene algún tipo de institucion, se le muestran todas las
        #denuncias de su zona, usuario dirigido a COCODES.
        if tipo == 'NG':
            denuncias = Denuncia.objects.filter(direccion=zona).order_by('-fecha')
        #Si no, se filtran por institucion.
        else:
            denuncias = Denuncia.objects.filter(
                # direccion=zona,
                motivo__institucion=institucion
                ).order_by('-fecha')

            #También se filtran los motivos relacionados a su institucion
            motivos = motivos.filter(institucion=institucion)

            #Si el usuario es de tipo 'respuesta', se filtran las denuncias
            #por las de los ultimos siete dias. Se aplican las mismas reglas
            #que de los usuarios de analisis.
            if request.user.is_res:
                fecha_hasta = timezone.now()+timedelta(days=1)
                fecha_desde = timezone.now()-timedelta(days=8)
                denuncias = denuncias.filter(
                        fecha__range=(
                            fecha_desde,
                            fecha_hasta)
                            )

    #La vista tiene una seccion de busquedas, eston son los parametros.
    # Cabe destacar que los filtros se aplican uno sobre otro.
    if request.GET:
        #Si se busca por año.
        #ej: Todas las denuncias del 2016.
        try:
            denuncias = denuncias.filter(fecha__year=request.GET['año'])
        except:
            pass
        #Si se busca por mes.
        #ej: Todas las denuncias de febrero.
        try:
            denuncias = denuncias.filter(fecha__month=request.GET['mes'])
        except:
            pass
        #Si se busca por dia.
        #ej: Todas las denuncias de la fecha 16.
        try:
            denuncias = denuncias.filter(fecha__day=request.GET['dia'])
        except:
            pass
        #Si se busca por motivo.
        #ej: Todas las denuncias por Robo.
        try:
            denuncias = denuncias.filter(motivo__id=request.GET['motivo'])
        except:
            pass
        #Si se busca por institucion. Este filtro solo aplica para COCODES y SU.
        #ej: Todas las denuncias dirigidas a PNC.
        try:
            if request.user.is_staff or tipo == 'NG':
                denuncias = denuncias.filter(motivo__instituciones=request.GET['institucion'])
            else:
                denuncias = denuncias.filter(motivo__instituciones=request.user.institucion)
            # errores.append('Institucion:' + str(
            #                         Institucion.objects.get(request.GET['motivo'])))
        except:
            pass

    #Si no hay respuesta, se muestra un error de "no coincidencias".
    if len(denuncias) == 0:
        messages.error(request, 'No existen coincidencias con esos parametros.')
        # for error in errores:
        #     messages.error(request, error)

    context = {
        "denuncias": denuncias,
        "motivos": motivos
    }

    #Si es SU o COCODE, se mandan todas las instituciones para hacer busquedas.
    if request.user.is_staff or tipo == 'NG':
        context.update({
            "instituciones": Institucion.objects.all()
        })


    return render(request,'usuario/denuncias_list.html', context)

"""
Clase de vista generica, sirve para visualizar los detalles de la denuncia,
aplicando sus filtros correspondientes.

--------------------------------------------------------------------------------
|     VARIABLE     |       TIPO      |              DESCRIPCION                |
-------------------+-----------------+------------------------------------------
|       model      |      Model      |  Indica sobre que modelo se va a basar  |
|                  |                 |  la vista, en este caso es una vista de |
|                  |                 |  'Denuncia'.                            |
--------------------------------------------------------------------------------
|     login_url    |      String     |  Contiene el nombre de la url de inicio |
|                  |                 |  de sesión.                             |
--------------------------------------------------------------------------------
|   template_name  |      String     |  Es la ruta de la plantilla             |
|                  |                 |  correspondiente a la vista.            |
--------------------------------------------------------------------------------
|     dispatch     |     funcion     |  Define la forma en que se visualiza la |
|                  |                 |  vista. Está decorado con               |
|                  |                 |  'login_required', para obligar al      |
|                  |                 |  usuario a iniciar sesión al ingresar a |
|                  |                 |  la vista.                              |
--------------------------------------------------------------------------------
| get_context_data |     funcion     |  Actualiza el diccionario de la vista.  |
--------------------------------------------------------------------------------
"""
class DenunciaDetail(DetailView):
    model = Denuncia
    login_url = 'inicio'
    template_name = 'usuario/denuncia_detail.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #Se obtiene el manejador de la funcion sin sobreescribir.
        handler = super(DenunciaDetail, self).dispatch(request, *args, **kwargs)

        #Se guarda al usuario.
        user = request.user
        #Se guarda el objeto que se va a mostrar.
        objeto = self.get_object(self.get_queryset())

        #Aplican filtros de permisos.
        #Si no es SU
        if not user.is_staff:
            #Si es Admin y COCODE
            if user.is_admin and user.institucion.tipo == 'NG':
                #Si no coincide con su direccion y su municipio
                if objeto.direccion != user.zona:
                    if objeto.direccion.municipio != user.zona.municipio:
                        #Se lanza un 404
                        raise Http404('error')
            #Si no es COCODE
            else:
                #Y no coinciden las instituciones, se lanza un 404
                if objeto.motivo.instituciones != user.institucion:
                    raise Http404('error')

                #Si es de Respuesta, y supera el limite de tiempo, se lanza 404.
                fecha_limite = timezone.now()-timedelta(days=8)
                if user.is_res and objeto.fecha < fecha_limite:
                    raise Http404('error')

        #Se retorna el manejador.
        return handler

    def get_context_data(self, **kwargs):
        #Se obtiene el contexto de la vista.
        context = super(DenunciaDetail, self).get_context_data(**kwargs)

        #Se guarda el objeto.
        objeto = self.get_object(self.get_queryset())
        #Se utilza una bandera para especificar el uso de Google Maps.
        #Si la denuncia no tiene coordenadas o estan a 0, se pone falso
        #y no se utilizan los mapas.
        geo = False
        if objeto.latitud is not None and objeto.longitud is not None:
            if objeto.latitud != 0 and objeto.longitud != 0:
                geo = True

        #Se actualiza el diccionario del contexto.
        #El indice 'label' se utiliza para mandar la primer letra del motivo
        #y utilizarlo en el marcador del mapa.
        context.update({
            "geo": geo,
            "label": objeto.motivo.motivo[0]
        })

        #Se retorna el diccionario
        return context
