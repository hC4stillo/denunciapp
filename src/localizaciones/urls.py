from django.conf.urls import url, include

from tastypie.api import Api

from .views import (
        busquedaM,
        busquedaD,
        obtenerD,
        estadisticas,
        municipioDetail,
        detalleZona,
        respuesta_municipio
        )
from .api import (
        DepartamentoResource,
        MunicipioResource,
        DireccionResource
        )

local_api = Api(api_name='local')
local_api.register(DepartamentoResource())
local_api.register(MunicipioResource())
local_api.register(DireccionResource())

urlpatterns = [

    url(r'^busqM/',busquedaM, name='muni'),
    url(r'^busqD/', busquedaD, name = 'dirs'),
    url(r'^obtD/', obtenerD, name='dens'),
    url(r'^muni_response/', respuesta_municipio, name='respuesta_municipio'),
    url(r'^$',estadisticas, name="estadisticas"),
    url(r'^detalleZona/', detalleZona, name='detalleZona'),
    url(r'^(?P<dep>\w+)/(?P<muni>\w+)$',municipioDetail,name='mDetail'),
    url(r'^api/', include(local_api.urls)),
]
