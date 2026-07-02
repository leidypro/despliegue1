from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages

class CreLoginView(LoginView):
    template_name = 'login/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        # Bloquear usuarios inactivos
        if not user.estado:
            form.add_error(None, "El usuario no se encuentra activo")
            return self.form_invalid(form)  # vuelve a renderizar el formulario con el error
        
        messages.success(self.request,f"Bienvenido Usuario {user.nombre}",extra_tags='login')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app:dashboard')
