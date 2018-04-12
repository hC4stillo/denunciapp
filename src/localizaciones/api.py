from tastypie.resources import (
                        ModelResource,
                        ALL,
                        ALL_WITH_RELATIONS
                        )
from tastypie.authorization import Authorization
from tastypie import fields

from .models import Departamento, Municipio, Direccion
from denuncia.models import Denuncia

class DepartamentoResource(ModelResource):

    def dehydrate(self, bundle):
        bundle.data['denuncias'] = bundle.obj.sumMunicipios()
        bundle.data['CR'] = Denuncia.objects.filter(
                                    tipo='CR',
                                    direccion__municipio__departamento=bundle.obj
                                    ).count()
        bundle.data['MU'] = Denuncia.objects.filter(
                                    tipo='MU',
                                    direccion__municipio__departamento=bundle.obj
                                    ).count()
        bundle.data['MA'] = Denuncia.objects.filter(
                                    tipo='MA',
                                    direccion__municipio__departamento=bundle.obj
                                    ).count()
        bundle.data['DH'] = Denuncia.objects.filter(
                                    tipo='DH',
                                    direccion__municipio__departamento=bundle.obj
                                    ).count()
        return bundle

    class Meta:
        queryset = Departamento.objects.all()
        resource_name = 'departamento'
        filtering = {
            'id': ALL,
        }
        allowed_methods = ['get']

class MunicipioResource(ModelResource):

    departamento = fields.ForeignKey(
                    DepartamentoResource,
                    attribute='departamento',
                    full=True,
                    )

    class Meta:
        queryset = Municipio.objects.all()
        resource_name = 'municipio'
        filtering = {
            'departamento': ALL_WITH_RELATIONS,
            'id': ALL,
        }
        allowed_methods = ['get']

class DireccionResource(ModelResource):

    municipio = fields.ForeignKey(
        MunicipioResource,
        attribute='municipio',
        full=True
    )

    class Meta:
        queryset = Direccion.objects.all()
        resource_name = 'direccion'
        filtering = {
            'municipio': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']
