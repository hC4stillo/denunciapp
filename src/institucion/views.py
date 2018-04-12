from django.shortcuts import render
from django.views.generic.detail import DetailView

from .models import Institucion, Sede, Correo, Telefono

# def lista(request):
#     instituciones = Institucion.objects.all()
#     return render(request,"institucion_list.html", {"instituciones":instituciones})
#
# class InstitucionDetail(DetailView):
#     model = Institucion
#     template_name = 'institucion_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(InstitucionDetail,self).get_context_data(**kwargs)
#         vID = kwargs['object']
#         print vID
#         correos = Correo.objects.filter(institucion=vID)
#         # sedes = Sede.
#         print correos
#
#         context.update({
#             "correos": correos,
#             })
#
#         return context
