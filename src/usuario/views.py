# -*- coding: utf-8 -*-

# import collections
# import time
import calendar
from datetime import datetime, date, time, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import UserCreationForm, InicioForm, CambioPassForm
from .models import Usuario
from localizaciones.models import Departamento
from denuncia.models import Denuncia


@login_required(login_url="inicio")
def registro(request):

    if request.user.is_staff:

        form = UserCreationForm(request.POST or None)

        context = {
            "form": form,
            "departamentos": Departamento.objects.all()
        }

        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/')

        return render(request, 'usuario/registro.html', context)

    return render(request, 'error/permisos.html', {})


def inicio(request):
    if request.user.is_authenticated():

        return HttpResponseRedirect('/usuario')

    if request.POST:

        form = InicioForm(request.POST)

        if form.is_valid():

            username = request.POST['username']
            password = request.POST['password']

            usuario = authenticate(username = username, password = password)

            if usuario is not None:
                if usuario.is_active:
                    login(request, usuario)

                    context = {
                        "form": form
                    }

                    if request.GET:
                        if request.GET['next'] != '/logout':
                            return HttpResponseRedirect(request.GET['next'])

                    return redirect('usuario:privado')

                else:
                    messages.error(request, 'Usuario inactivo, comunicate con tu administrador.')
                    return HttpResponseRedirect('/')
            else:
                messages.error(request, 'La contraseña o el usuario no coinciden.')
                return HttpResponseRedirect('/')

        else:
            messages.error(request, 'Datos invalidos.')

    else:

        form = InicioForm()

        context = {
            "form": form
        }

        return render(request, 'usuario/inicio.html', context)

@login_required(login_url='inicio')
def cerrar(request):
    request.user.ultima_conexion = timezone.now()
    request.user.save()

    logout(request)
    return redirect('inicio')

def restarMeses(fecha, resta):
    if resta >= fecha.month:
        resta = resta - fecha.month

        nueva_fecha = fecha.replace(year=(fecha.year-1), month=(12-resta), day=1)

        # print resta
        # if resta > 12:
        #     nueva_fecha = restarMeses(nueva_fecha, resta)
        # else:
        #     nueva_fecha = nueva_fecha.replace(month=(12-resta))
    # elif resta == fecha.month:
    #     nueva_fecha = fecha.replace(month=1)
    else:
        nueva_fecha = fecha.replace(month=(fecha.month - resta), day=1)

    return nueva_fecha

def getDenuncias():
    dias = 31#timezone.now().day

    i=1
    # denuncias = collections.OrderedDict()
    denuncias = []
    fecha1 = restarMeses(timezone.now(), 1)
    fecha2 = restarMeses(timezone.now(), 2)
    while i<=dias:
        denuncias.append((
            str(i), len(Denuncia.objects.filter(
                fecha__year = timezone.now().year
            ).filter(
                fecha__month = timezone.now().month
            ).filter(
                fecha__day = i
            )), len(Denuncia.objects.filter(
                fecha__year = fecha1.year
            ).filter(
                fecha__month = fecha1.month
            ).filter(
                fecha__day = i
            )), len(Denuncia.objects.filter(
                fecha__year = fecha2.year
            ).filter(
                fecha__month = fecha2.month
            ).filter(
                fecha__day = i))))
        i += 1

    return denuncias

@login_required(login_url='inicio')
def privado(request):

    # print restarMeses(timezone.now(), 23)

    context = {
        'denuncias': getDenuncias(),
        'tiempo1': timezone.now().strftime('%B'),
        'tiempo2': calendar.month_name[restarMeses(timezone.now(), 1).month],
        'tiempo3': calendar.month_name[restarMeses(timezone.now(), 2).month]
    }

    return render(request, 'usuario/privado.html', context)


@login_required(login_url='inicio')
def usuarioList(request):

    if not request.user.is_staff:
        # return render(request, 'error/permisos.html', {})
        raise Http404('error')

    usuarios = Usuario.objects.exclude(id=request.user.id)

    if request.GET:
        if request.GET['institucion']:
            usuarios = usuarios.filter(
                        institucion__nombre=request.GET['institucion']
                        )

    if len(usuarios) == 0:
        raise Http404('error')

    context = {
        'usuarios': usuarios
    }

    return render(request, 'usuario/usuarios_list.html', context)

class UsuarioDetail(DetailView):
    model = Usuario
    login_url = 'inicio'
    template_name = 'usuario/usuario_detail.html'
    slug_field = 'username'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        handler = super(UsuarioDetail, self).dispatch(request, *args, **kwargs)

        if self.get_object(self.queryset) == request.user:
            return redirect('usuario:privado')

        if not request.user.is_staff:
            # return render(request, 'error/permisos.html', {})
            raise Http404('error')

        return handler


class UsuarioEdit(UpdateView):
    model = Usuario
    login_url = 'inicio'
    template_name = 'usuario/usuario_edit.html'
    slug_field = 'username'
    success_url = reverse_lazy('usuario:lista_u')

    fields = [
        'nombre',
        'apellidos',
        # 'correo',
        'is_staff',
        'is_admin',
        'is_res',
        'is_active',
        'institucion',
        'zona'
    ]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):

        handler = super(UsuarioEdit, self).dispatch(request, *args, **kwargs)

        if self.get_object(self.queryset) == request.user:
            return redirect('usuario:privado')

        if not request.user.is_staff:
            # return render(request, 'error/permisos.html', {})
            raise Http404('error')

        return handler

    def get_context_data(self, **kwargs):

    	context = super(UsuarioEdit, self).get_context_data(**kwargs)
    	Departamentos = Departamento.objects.all()

    	context.update({
    		"departamentos":Departamentos,
    		})

    	return context

@login_required(login_url='inicio')
def cambiarPass(request):
    if request.method == 'POST':
        form = CambioPassForm(request.POST)

        if form.is_valid():

            actual_pass = request.POST['actual']
            if request.user.check_password(actual_pass):
                nuevo_pass = request.POST['password1']

                if not request.user.check_password(nuevo_pass):

                    request.user.set_password(nuevo_pass)
                    request.user.save()

                    logout(request)
                    messages.info(request, 'Inicia sesión de nuevo porfavor.')
                    return redirect('inicio')
                else:
                    messages.error(request, 'No puedes usar tu actual contraseña.')

            else:
                messages.error(request, 'Primero ingresa tu contraseña actual.')
        else:
            messages.error(request, 'Ingresa correctamente los campos')
    else:
        form = CambioPassForm()

    return render(request, 'usuario/cambio_pass.html', {'form':form})

@login_required(login_url='inicio')
def confirmarPass(request):
    if request.GET:
        if request.method == 'POST':
            password = request.POST['password']

            if request.user.check_password(password):
                request.session['confirmado'] = True

                return HttpResponseRedirect(request.GET['next'])
            else:
                messages.error(request, 'Contraseña incorrecta.')

        return render(request, 'usuario/confirmarPass.html', {})

    else:
        return redirect('inicio')


@login_required(login_url='inicio')
def cambiarCorreo(request):
    try:
        confirmado = request.session['confirmado']
    except:
        confirmado = False

    if not confirmado:
        return HttpResponseRedirect('/confirmar/?next=%s' % request.path)
    else:

        if request.method == 'POST':
            correo = request.POST['correo']

            if correo == request.user.correo:
                messages.info(request, 'Ese es tu correo actual.')
            else:
                request.user.correo = correo
                request.user.save()
                request.session['confirmado'] = False

                logout(request)
                messages.info(request, 'Inicia sesión de nuevo porfavor.')

                # text_content = 'Denuncia'
                # html_content = '<body><h1></h1></body>
                #                     '''<footer><i>Los archivos quedan a cargo de la
                #                      entidad indicada.</i><br>
                #                     <i>Todos los datos de este correo son
                #                      confidenciales y no deben ser difundidos
                #                     a nadie más que las entidades interesadas
                #                      en ellos.</i></footer>'''
                #
                # from_email = '"Denuncia Movil" <denunciamovil@gmail.com>'
                # to = vIn
                # msg = EmailMultiAlternatives(motivo, text_content, from_email, to)
                # msg.attach_alternative(html_content, "text/html")
                # if request.FILES:
                #     msg.attach(archivo.name,archivo.read(),archivo.content_type)
                # msg.send()

                return redirect('inicio')

        return render(request, 'usuario/cambio_correo.html', {})
