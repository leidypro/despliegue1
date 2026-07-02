from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from app.models import tipoelemento
from app.forms import TipoElementoForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse


class TipoElementoListView(ListView):
    model = tipoelemento
    template_name = 'TipoElemento/index.html'
    context_object_name = 'tipos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Tipos de Elemento'
        context['subtitulo'] = 'Clasificación de inventario'
        context['crear_url'] = reverse_lazy('app:crear_elemento')
        context['limpiar_url'] = reverse_lazy('app:limpiar_tipo')
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class TipoElementoCreateView(CreateView):
    model = tipoelemento
    form_class = TipoElementoForm
    template_name = 'modals/modals_base.html'
    success_url = reverse_lazy('app:crear_inventario')


    def form_valid(self, form):
        self.object = form.save()
        mensaje_texto = 'Se creó un nuevo tipo de elemento'

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'nombre': str(self.object),
                'message': mensaje_texto
            })

        messages.success(self.request, mensaje_texto)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)


class TipoElementoUpdateView(UpdateView):
    model = tipoelemento
    form_class = TipoElementoForm
    template_name = 'TipoElemento/crear.html'
    success_url = reverse_lazy('app:index_tipo')
    def form_valid(self, form):
        messages.success(self.request, 'Se actualizo con exito')
        return super().form_valid(form)


class TipoElementoDeleteView(DeleteView):
    model = tipoelemento
    template_name = 'TipoElemento/eliminar.html'
    success_url = reverse_lazy('app:index_tipo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Tipo De Elemento'
        context['subtitulo'] = '¿Está seguro de eliminar este Tipo De Elemento?'
        context['listar_url'] = reverse_lazy('app:index_tipo')
        return context
    def form_valid(self, form):
        messages.success(
            self.request, 'Tipo de elemento  eliminado exitosamente.')
        return super().form_valid(form)

    success_url = reverse_lazy('app:crear_elemento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_url'] = reverse_lazy('app:crear_elemento')
        return context


class TipoCleandView(View):
    def post(self, request, *args, **kwargs):
        tipoelemento.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = tipoelemento._meta.db_table
            print(nombre_tabla)
            cursor.execute(
                f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';")

        messages.success(
            self.request, "Todos los cursos han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_tipo'))
