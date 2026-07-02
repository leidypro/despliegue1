from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from app.models import Usuario, Administrador, docente, Estudiante, Acudiente

from app.forms import UsuarioForm, UsuarioUpdateForm, AdministradorForm, DocenteForm, EstudianteForm, AcudienteForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.contrib.auth.models import Group

def asignar_grupo(usuario, rol):
    usuario.groups.clear()  # eliminar roles anteriores
    grupo = Group.objects.get(name=rol.capitalize())
    usuario.groups.add(grupo)
    
def validar_formulario_rol(rol, data, instance=None):
    """
    Valida el formulario según el rol.
    """
    if rol == 'administrador':
        form = AdministradorForm(data, instance=instance)
    elif rol == 'docente':
        form = DocenteForm(data, instance=instance)
    elif rol == 'estudiante':
        form = EstudianteForm(data, instance=instance)
    elif rol == 'acudiente':
        form = AcudienteForm(data, instance=instance)
    else:
        return False, None

    return form.is_valid(), form


def guardar_perfil_rol(usuario, rol, data):
    """Crea un perfil nuevo."""
    if rol == 'administrador':
        Administrador.objects.create(usuario=usuario, cargo=data.get('cargo'))
    elif rol == 'docente':
        docente.objects.create(
            usuario=usuario, especialidad=data.get('especialidad'))
    elif rol == 'estudiante':
        Estudiante.objects.create(
            usuario=usuario,
            codigo=data.get('codigo'),
            fechaNacimiento=data.get('fechaNacimiento'),
            estadoMatricula=data.get('estadoMatricula'),
            fechaIngreso=data.get('fechaIngreso'),
            cursoId_id=data.get('cursoId')
        )
    elif rol == 'acudiente':
        Acudiente.objects.create(usuario=usuario, telefono=data.get(
            'telefono'), direccion=data.get('direccion'))
    
    asignar_grupo(usuario,rol)
# --- VISTAS ---


class UsuarioListView(ListView):
    model = Usuario
    template_name = 'usuario/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Usuarios'
        context['subtitulo'] = 'Bienvenido al listado de usuarios'
        context['crear_url'] = reverse_lazy('app:crear_usuario')
        context['limpiar_url'] = reverse_lazy('app:limpiar_usuario')
        context['table'] = "Usuarios"
        context['text'] = "Usuarios con estado inactivo"
        context['total_text'] = "Total de Usuarios"
        context['table'] = "Usuarios"
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class UsuarioCreateView(View):
    template_name = 'usuario/crear.html'
    success_url = reverse_lazy('app:index_usuario')

    def get_context(self, **kwargs):
        context = {
            'usuario_form': UsuarioForm(),
            'admin_form': AdministradorForm(),
            'docente_form': DocenteForm(),
            'estudiante_form': EstudianteForm(),
            'acudiente_form': AcudienteForm(),
            'titulo': 'Crear Usuario',
            'listar_url': reverse_lazy('app:index_usuario'),
            'rol_actual': '',
            'btn_name': 'Guardar'
        }
        context.update(kwargs)
        return context

    def get(self, request):
        return render(request, self.template_name, self.get_context())

    @transaction.atomic
    def post(self, request):
        # Esto muestra todos los archivos enviados
        usuario_form = UsuarioForm(request.POST, request.FILES)
        print(request.FILES)
        rol = request.POST.get('rol')
        if rol == 'estudiante':
            rol_form = EstudianteForm(request.POST, request.FILES)
        elif rol == 'docente':
            rol_form = DocenteForm(request.POST, request.FILES)
        elif rol == 'administrador':
            rol_form = AdministradorForm(request.POST, request.FILES)
        elif rol == 'acudiente':
            rol_form = AcudienteForm(request.POST, request.FILES)
        else:
            rol_form = None

        print("FORM USUARIO VALIDO:", usuario_form.is_valid())
        print("FORM ROL VALIDO:", rol_form.is_valid() if rol_form else None)
        print("ERRORES ROL:", rol_form.errors if rol_form else None)

        if usuario_form.is_valid() and rol_form and rol_form.is_valid():

            usuario = usuario_form.save(commit=False)
            usuario.set_password(usuario_form.cleaned_data['password'])
            usuario.save()

            perfil = rol_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            asignar_grupo(usuario, rol)
            messages.success(request, 'Usuario creado correctamente')
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            self.get_context(
                usuario_form=usuario_form,
                rol_actual=rol
            )
        )


class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'usuario/crear.html'
    success_url = reverse_lazy('app:index_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.object
        context.update({
            'titulo': 'Editar Usuario',
            'listar_url': self.success_url,
            'usuario_form': context.get('form'),
            'admin_form': AdministradorForm(),
            'docente_form': DocenteForm(),
            'estudiante_form': EstudianteForm(),
            'acudiente_form': AcudienteForm(),
            'btn_name': 'Actualizar'
        })

        # Cargar perfiles existentes para mostrar datos en los campos
        admin = Administrador.objects.filter(usuario=usuario).first()
        if admin:
            context.update({'rol_actual': 'administrador',
                           'admin_form': AdministradorForm(instance=admin)})

        doc = docente.objects.filter(usuario=usuario).first()
        if doc:
            context.update(
                {'rol_actual': 'docente', 'docente_form': DocenteForm(instance=doc)})

        est = Estudiante.objects.filter(usuario=usuario).first()
        if est:
            context.update({'rol_actual': 'estudiante',
                           'estudiante_form': EstudianteForm(instance=est)})

        acu = Acudiente.objects.filter(usuario=usuario).first()
        if acu:
            context.update({'rol_actual': 'acudiente',
                           'acudiente_form': AcudienteForm(instance=acu)})

        return context

    def form_valid(self, form):
        usuario = form.save()
        nuevo_rol = self.request.POST.get('rol')

        # Buscar qué perfil tiene actualmente el usuario
        p_admin = Administrador.objects.filter(usuario=usuario).first()
        p_doc = docente.objects.filter(usuario=usuario).first()
        p_est = Estudiante.objects.filter(usuario=usuario).first()
        p_acu = Acudiente.objects.filter(usuario=usuario).first()

        perfil_previo = p_admin or p_doc or p_est or p_acu

        # Identificar la instancia que coincide con el rol seleccionado
        instancia_a_validar = None
        if nuevo_rol == 'administrador':
            instancia_a_validar = p_admin
        elif nuevo_rol == 'docente':
            instancia_a_validar = p_doc
        elif nuevo_rol == 'estudiante':
            instancia_a_validar = p_est
        elif nuevo_rol == 'acudiente':
            instancia_a_validar = p_acu

        # Validar pasando la instancia para que Django sepa que es una EDICIÓN
        valido, rol_form = validar_formulario_rol(
            nuevo_rol, self.request.POST, instance=instancia_a_validar)

        if not valido:
            messages.error(self.request, 'Errores en los campos del perfil.')
            return self.render_to_response(self.get_context_data(form=form))

        # Lógica de guardado
        if perfil_previo and instancia_a_validar is None:

            perfil_previo.delete()
            guardar_perfil_rol(usuario, nuevo_rol, self.request.POST)
        else:

            obj = rol_form.save(commit=False)
            obj.usuario = usuario
            obj.save()
        asignar_grupo(usuario, nuevo_rol)
        messages.success(self.request, 'Usuario actualizado correctamente')
        return redirect(self.success_url)


class UsuarioDetailView(View):
    def get(self, request, pk):
        usuario = Usuario.objects.get(pk=pk)

        data = {
            'nombre': usuario.nombre,
            'email': usuario.email,
            'rol': str(usuario.get_rol()),
            'estado': 'Activo' if usuario.estado else 'Inactivo',
            'fecha_creacion': usuario.fecha_creacion
        }

        return JsonResponse(data)


class UsuarioCleandView(View):
    def post(self, request, *args, **kwargs):
        Usuario.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Usuario._meta.db_table
            cursor.execute(
                f"ALTER TABLE {nombre_tabla} auto_increment = 1;")

        messages.success(
            self.request, "Todos los Usuarios han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_usuario'))


class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = 'usuario/eliminar.html'
    success_url = reverse_lazy('app:index_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Usuario'
        context['subtitulo'] = '¿Está seguro de eliminar este usuario?'
        context['listar_url'] = reverse_lazy('app:index_usuario')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Usuario eliminado exitosamente.')
        return super().form_valid(form)


class PerfilView(LoginRequiredMixin, View):
    template_name = "modals/perfil.html"

    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user
        })

    def post(self, request):
        usuario = request.user
        errores = []

        nombre = request.POST.get('nombre', '').strip()
        print("nombre", nombre)
        if nombre:
            usuario.nombre = nombre
            print("nombre recibido", usuario.nombre)
        else:
            errores.append('El nombre no puede estar vacío.')
        if 'img_usuario' in request.FILES:
            foto = request.FILES['img_usuario']
            tipos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
            if foto.content_type not in tipos_permitidos:
                errores.append('Solo se permiten imágenes JPG, PNG o WEBP.')
            elif foto.size > 5 * 1024 * 1024:
                errores.append('La imagen no puede superar 5MB.')
            else:
                usuario.img_usuario = foto

        password = request.POST.get('password', '').strip()
        if password:
            if len(password) < 8:
                errores.append(
                    'La contraseña debe tener al menos 8 caracteres.')
            else:
                usuario.set_password(password)

        if errores:
            return JsonResponse({'success': False, 'message': ' '.join(errores)})

        try:
            usuario.save()
            if password and len(password) >= 8:
                update_session_auth_hash(request, usuario)
            return JsonResponse({'success': True, 'message': 'Perfil actualizado correctamente.' , 'nombre':usuario.nombre})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error al guardar los cambios.'})