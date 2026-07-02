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


def listar_movimiento(request):
    movimiento = Movimiento.objects.all()
    return render(request, 'movimiento/index.html', {'movimientos': movimiento})


class MovimientoListView(ListView):
    model = Movimiento
    template_name = 'movimiento/index.html'
    context_object_name = 'movimientos'
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
        context['titulo'] = 'Listado de Movimientos'
        context['subtitulo'] = 'Bienvenido al listado de Movimientos'
        context['crear_url'] = reverse_lazy('app:crear_movimiento')
        context['limpiar_url'] = reverse_lazy('app:limpiar_movimiento')
        context['table'] = "movimiento"  
        context['text'] = "Movimientos de Hoy"
        context['total_text'] = "Total de Movimientos"
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class MovimientoCreateView(CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'movimiento/crear.html'

    success_url = reverse_lazy('app:index_movimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Movimiento"
        context['listar_url'] = reverse_lazy('app:index_movimiento')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Movimiento creado correctamente")
        return super().form_valid(form)


class MovimientoupdateView(UpdateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'movimiento/crear.html'
    success_url = reverse_lazy('app:index_movimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Movimiento"
        context['listar_url'] = reverse_lazy('app:index_movimiento')
        context['btn_name'] = "Actualizar"
        return context
    
    def form_valid(self, form):
        messages.success(self.request,"Movimiento actualizado correctamente")
        return super().form_valid(form)


class MovimientoDeleteView(DeleteView):
    model = Movimiento
    template_name = 'movimiento/eliminar.html'
    success_url = reverse_lazy('app:index_movimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar Movimiento"
        context['listar_url'] = reverse_lazy('app:index_movimiento')
        return context


    def form_valid(self, form):
        messages.success(self.request, "Movimiento eliminado correctamente")
        return super().form_valid(form)

class MovimientoCleandView(View):
   def post(self, request, *args, **kwargs):
        Movimiento.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Movimiento._meta.db_table
            print(nombre_tabla)
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';")
        
        messages.success(self.request, "Todos los Movimientos han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_movimiento'))