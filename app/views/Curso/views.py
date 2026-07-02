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

# Ejemplo Listar_Usuarios


def listar_usuario(request):
    usuario = Usuario.objects.all()
    return render(request, 'usuario/index.html', {'usuarios': usuario})


def listar_curso(request):
    curso = Curso.objects.all()
    return render(request, 'curso/index.html', {'cursos': curso})


class CursoListView(ListView):
    model = Curso
    template_name = 'curso/index.html'
    context_object_name = 'cursos'
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
        context['titulo'] = 'Listado de Cursos'
        context['subtitulo'] = 'Bienvenido al listado de cursos'
        context['crear_url'] = reverse_lazy('app:crear_curso')
        context['text'] = "Cursos con estado inactivo"
        context['total_text'] = "Total de Cursos"
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class CursoCreateView(CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'curso/crear.html'

    success_url = reverse_lazy('app:index_curso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Curso"
        context['listar_url'] = reverse_lazy('app:index_curso')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Curso creado correctamente")
        return super().form_valid(form)


class CursoupdateView(UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'curso/crear.html'
    success_url = reverse_lazy('app:index_curso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Curso"
        context['listar_url'] = reverse_lazy('app:index_curso')
        context['btn_name'] = "Actualizar"
        return context
    
    def form_valid(self, form):
        messages.success(self.request,"Curso actualizado correctamente")
        return super().form_valid(form)


class CursoDeleteView(DeleteView):
    model = Curso
    template_name = 'curso/eliminar.html'
    success_url = reverse_lazy('app:index_curso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar Curso"
        context['listar_url'] = reverse_lazy('app:index_curso')
        return context


    def form_valid(self, form):
        messages.success(self.request, "Curso eliminado correctamente")
        return super().form_valid(form)

class CursoCleandView(View):
   def post(self, request, *args, **kwargs):
        Curso.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Curso._meta.db_table
            print(nombre_tabla)
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';")
        
        messages.success(self.request, "Todos los cursos han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_curso'))