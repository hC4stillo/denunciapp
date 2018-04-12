"""Denuncias URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin

from denuncia.views import busquedaMo

urlpatterns = [
    url(r'^a84cdb3a7c1d949ede1fc3a72a1e781d3f4de971/', admin.site.urls),
    url(r'^logout/', 'usuario.views.cerrar', name='logout'),
    url(r'^usuario/', include('usuario.urls', namespace='usuario')),
    url(r'^institucion/', include('institucion.urls', namespace='institucion')),
    url(r'^$', 'usuario.views.inicio',name='inicio'),
    url(r'^denunciar/','denuncia.views.denunciar',name='denunciar'),
    url(r'^denuncias/', include('denuncia.urls', namespace='denuncias')),
    url(r'^success/', 'denuncia.views.success', name = 'success'),
    url(r'^busqMot/', busquedaMo, name='mots'),
    url(r'^estadisticas/', include('localizaciones.urls', namespace="local")),
    url(r'^mapa/','localizaciones.views.mapa',name="mapa"),
    url(r'^confirmar/', 'usuario.views.confirmarPass', name='confirmarPass'),
    url(r'^push/', include('gcm.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
else:
    urlpatterns += url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),
