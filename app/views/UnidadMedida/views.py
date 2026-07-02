from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from app.models import UnidadMedida
from app.forms import UnidadMedidaForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
class UnidadMedidaListView(ListView):
    model = UnidadMedida
    template_name = 'UnidadMedida/index.html'
    context_object_name = 'unidades'
    success_url = reverse_lazy('app:index_unidad')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Unidades de Medida'
        context['subtitulo'] = 'Gestión de unidades para inventario'
        context['crear_url'] = reverse_lazy('app:crear_unidad')
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context

class UnidadMedidaCreateView(CreateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'modals/modals_base.html'
    success_url = reverse_lazy('app:index_unidad')
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
    

class UnidadMedidaUpdateView(UpdateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'UnidadMedida/crear.html'
    success_url = reverse_lazy('app:index_unidad')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_url'] = reverse_lazy('app:index_unidad')
        context['btn_name'] = "Actualizar"
        return context
    def form_valid(self, form):
        messages.success(self.request, "Unidad de medida actualizada correctamente")
        return super().form_valid(form)


class UnidadMedidaDeleteView(DeleteView):
    model = UnidadMedida
    template_name = 'UnidadMedida/eliminar.html'
    success_url = reverse_lazy('app:index_unidad')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Unidad de Medida'
        context['subtitulo'] = '¿Está seguro de eliminar esta Unidad de medida?'
        context['redirect'] = reverse_lazy('app:index_unidad')
        return context
    def form_valid(self, form):
        messages.success(self.request, "Unidad de medida eliminada correctamente")
        return super().form_valid(form)
