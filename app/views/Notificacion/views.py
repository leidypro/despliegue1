from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView , View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from app.models import *
from app.forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
# Create your views here.
def index(request):
    return render(request, 'index.html')

# Ejemplo Listar_UsuarioS
def listar_usuario(request):
    usuario = Usuario.objects.all()
    return render(request, 'usuario/index.html', {'usuarios': usuario})


def listar_notificacion(request):
    notificacion = Notificacion.objects.all()
    return render(request, 'notificacion/index.html', {'notificaciones': notificacion})


class NotificacionListView(ListView):
    model = Notificacion
    template_name = 'notificacion/index.html'
    context_object_name = 'notificacion'
    # Uso de DICCIONARIOS
    # Metodo Dispatch
    # @method_decorator(login_required)

    def dispatch(self, request, *args, **kwargs):
        # if request.method == "GET":
        # return redirect('app:listar_curso')
        return super().dispatch(request, *args, **kwargs)
# metodo Post

    def post(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Herencia por medio de super
        context['titulo'] = 'Listado de Notificaciones'
        context['subtitulo'] = 'Bienvenido al listado de Notificaciones'
        context['crear_url'] = reverse_lazy('app:crear_notificacion')
        context['limpiar_url'] = reverse_lazy('app:limpiar_notificacion')
        context['table'] = "notificacion"  
        context['text'] = "Notificaciones de Hoy"
        context['total_text'] = "Total de Notificaciones"
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class NotificacionCreateView(CreateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'notificacion/crear.html'

    success_url = reverse_lazy('app:index_notificacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear notificacion"
        context['listar_url'] = reverse_lazy('app:index_notificacion')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "notificacion creada correctamente")
        return super().form_valid(form)


class NotificacionupdateView(UpdateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'notificacion/crear.html'
    success_url = reverse_lazy('app:index_notificacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Notificacion"
        context['listar_url'] = reverse_lazy('app:index_notificacion')
        context['btn_name'] = "Actualizar"
        return context
    
    def form_valid(self, form):
        messages.success(self.request,"notificacion actualizada correctamente")
        return super().form_valid(form)


class NotificacionDeleteView(DeleteView):
    model = Notificacion
    template_name = 'notificacion/eliminar.html'
    success_url = reverse_lazy('app:index_notificacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar notificacion"
        context['listar_url'] = reverse_lazy('app:index_notificacion')
        return context


    def form_valid(self, form):
        messages.success(self.request, "notificacion eliminada correctamente")
        return super().form_valid(form)

class NotificacionCleandView(View):
   def post(self, request, *args, **kwargs):
        Notificacion.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Notificacion._meta.db_table
            print(nombre_tabla)
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';")
        
        messages.success(self.request, "Todas las notificaciones han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_notificacion')) 