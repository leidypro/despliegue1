from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group



@receiver(post_migrate)
def registrar_rol(sender, **kwargs):
    grupos = ['Administrador', 'Docente', 'Estudiante', 'Acudiente']
    for nombre in grupos:
        Group.objects.get_or_create(name=nombre)
@receiver(post_migrate)
def asignar_permisos(sender,**kwargs):
    content_type = ContentType.objects.get_for_model(Usuario)

    permisos = Permission.objects.filter(content_type=content_type)

    admin = Group.objects.get(name='Administrador')
    docente = Group.objects.get(name='Docente')

    # 🔴 ADMIN: todos los permisos
    admin.permissions.set(permisos)

    # 🔵 DOCENTE: solo ver y editar
    docente.permissions.set(
        Permission.objects.filter(
            codename__in=['view_usuario', 'change_usuario']
        )
    )