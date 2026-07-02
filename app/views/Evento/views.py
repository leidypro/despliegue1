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


def listar_evento(request):
    evento = Evento.objects.all()
    return render(request, 'evento/index.html', {'eventos': evento})



class EventoListView(ListView):
    model = Evento
    template_name = 'evento/index.html'
    context_object_name = 'eventos'
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
        context['titulo'] = 'Listado de Eventos'
        context['subtitulo'] = 'Bienvenido al listado de Eventos'
        context['crear_url'] = reverse_lazy('app:crear_evento')
        context['limpiar_url'] = reverse_lazy('app:limpiar_evento')
        context['table'] = "evento"  
        context['text'] = "Eventos de Hoy"
        context['total_text'] = "Total de Eventos"
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context
    

class EventoCreateView(CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento/crear.html'

    success_url = reverse_lazy('app:index_evento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Evento"
        context['listar_url'] = reverse_lazy('app:index_evento')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Evento creado correctamente")
        return super().form_valid(form)


class EventoupdateView(UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento/crear.html'
    success_url = reverse_lazy('app:index_evento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Evento"
        context['listar_url'] = reverse_lazy('app:index_evento')
        context['btn_name'] = "Actualizar"
        return context
    
    def form_valid(self, form):
        messages.success(self.request,"Evento actualizado correctamente")
        return super().form_valid(form)


class EventoDeleteView(DeleteView):
    model = Evento
    template_name = 'evento/eliminar.html'
    success_url = reverse_lazy('app:index_evento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar Evento"
        context['listar_url'] = reverse_lazy('app:index_evento')
        return context


    def form_valid(self, form):
        messages.success(self.request, "Evento eliminado correctamente")
        return super().form_valid(form)

class EventoCleandView(View):
   def post(self, request, *args, **kwargs):
        Evento.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Evento._meta.db_table
            print(nombre_tabla)
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';")
        
        messages.success(self.request, "Todos los Eventos han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_evento'))