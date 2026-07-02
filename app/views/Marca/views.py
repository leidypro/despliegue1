from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from app.models import marca
from app.forms import MarcaForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse


def listar_marca(request):
    marcas = marca.objects.all()
    return render(request, 'Marca/index.html', {'marcas': marcas})


class marcaListView(ListView):
    model = marca
    template_name = 'Marca/index.html'
    context_object_name = 'marcas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Marcas'
        context['subtitulo'] = 'Gestión de marcas para inventario'
        context['crear_url'] = reverse_lazy('app:crear_marca')
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class marcaCreateView(CreateView):
    model = marca
    form_class = MarcaForm
    template_name = 'modals/modals_base.html'
    success_url = reverse_lazy('app:crear_elemento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_url'] = reverse_lazy('app:index_unidad')
        context['btn_name'] = "Guardar"
        return context
    def form_valid(self, form):
        self.object = form.save()
        mensaje_texto = 'Se creo un nueva Unidad de Medida'
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success' : True,
                'id':self.object.id,
                'nombre':str(self.object),
                'message' : mensaje_texto
            })
        return super().form_valid(form)
    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'succes' : False,
                'errors': form.errors
            },status=400)
        return super().form_invalid(form)
class marcaUpdateView(UpdateView):
    model = marca
    form_class = MarcaForm
    template_name = 'Marca/crear.html'
    success_url = reverse_lazy('app:crear_elemento')

    def form_valid(self, form):
        messages.success(self.request, "Marca actualizada correctamente")
        return super().form_valid(form)

class marcaDeleteView(DeleteView):
    model = marca
    template_name = 'Marca/eliminar.html'
    success_url = reverse_lazy('app:crear_elemento')

    def form_valid(self, form):
        messages.success(self.request, "Marca eliminada correctamente")
        return super().form_valid(form)
