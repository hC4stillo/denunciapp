from django.conf.urls import url, include
from tastypie.api import Api

from .api import InstitucionResource, CorreoResource

v1_api = Api(api_name='v1')
v1_api.register(InstitucionResource())
v1_api.register(CorreoResource())

urlpatterns = [

    url(r'^api/', include(v1_api.urls)),

]
