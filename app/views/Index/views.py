from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from app.models import Usuario
from django.urls import reverse_lazy
from app.mixins import RolMixin
class DashboardView(LoginRequiredMixin,RolMixin, TemplateView):
    template_name = 'index/dashboard.html'
    login_url = reverse_lazy('app:login')
    roles_permitidos = ['Administrador', 'Docente']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['usuario_nombre'] = user.nombre
        context['usuario_rol'] = user.get_rol()
        context['usuario_estado'] = 'Activo' if user.estado else 'Inactivo'

        # Estadísticas rápidas
        context['total_usuarios'] = Usuario.objects.count()
        context['total_docentes'] = getattr(Usuario.objects.filter(docente__isnull=False), 'count', lambda: 0)()
        context['total_estudiantes'] = getattr(Usuario.objects.filter(estudiante__isnull=False), 'count', lambda: 0)()
        context['total_acudientes'] = getattr(Usuario.objects.filter(acudiente__isnull=False), 'count', lambda: 0)()

        # Últimas acciones (ejemplo)
        context['ultimas_acciones'] = [
            "Juan Pérez inició sesión",
            "María López actualizó su perfil",
            "Pedro Gómez creó un nuevo usuario"
        ]

        return context

class Qr_code(TemplateView):
    template_name = "escaner/escaner.html"