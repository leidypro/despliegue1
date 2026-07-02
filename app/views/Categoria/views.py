from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from app.models import categoria
from app.forms import CategoriaForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse

class CategoriaListView(ListView):
    model = categoria
    template_name = 'Categoria/index.html'
    context_object_name = 'categorias'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Categorías'
        context['subtitulo'] = 'Gestión de categorías para inventario'
        context['crear_url'] = reverse_lazy('app:crear_categoria')
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class CategoriaCreateView(CreateView):
    model = categoria
    form_class = CategoriaForm
    template_name = 'modals/modals_base.html'
    success_url = reverse_lazy('app:index_categoria')  # cambia si tu listado tiene otro nombre
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

class CategoriaUpdateView(UpdateView):
    model = categoria
    form_class = CategoriaForm
    template_name = 'Categoria/crear.html'
    success_url = reverse_lazy('app:index_categoria')  # cambia si tu listado tiene otro nombre
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Categoría"
        context['listar_url'] = reverse_lazy('app:index_categoria')
        context['btn_name'] = "Actualizar"
        return context
    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada correctamente")
        return super().form_valid(form)
    
class CategoriaDeleteView(DeleteView):  
    model = categoria
    template_name = 'Categoria/eliminar.html'
    success_url = reverse_lazy('app:index_categoria')  # cambia si tu listado tiene otro nombre

    def form_valid(self, form):
        messages.success(self.request, "Categoría eliminada correctamente")
        return super().form_valid(form)