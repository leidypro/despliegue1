from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from app.models import (
    Notificacion, Movimiento, Elemento, UnidadMedida,
    marca, categoria, tipoelemento,
    Estudianteacudiente, Asistencia,
    Estudiante, Acudiente, Curso, docente,
    Evento, Administrador, Usuario
)

class Command(BaseCommand):
    help = 'Limpia la base de datos y carga 10 datos de prueba'

    def handle(self, *args, **kwargs):

        # =====================
        # LIMPIAR BASE DE DATOS
        # =====================
        Notificacion.objects.all().delete()
        Movimiento.objects.all().delete()
        Elemento.objects.all().delete()
        UnidadMedida.objects.all().delete()
        marca.objects.all().delete()
        categoria.objects.all().delete()
        tipoelemento.objects.all().delete()
        Estudianteacudiente.objects.all().delete()
        Asistencia.objects.all().delete()
        Estudiante.objects.all().delete()
        Acudiente.objects.all().delete()
        Curso.objects.all().delete()
        docente.objects.all().delete()
        Evento.objects.all().delete()
        Administrador.objects.all().delete()
        Usuario.objects.all().delete()

        self.stdout.write(self.style.WARNING('✔ Base de datos limpiada'))

        # =====================
        # ADMINISTRADOR
        # =====================
        admin_user = Usuario.objects.create(
            nombre='Administrador',
            email='admin@mail.com',
            contraseña='123456',
            estado=True
        )

        admin = Administrador.objects.create(
            usuario=admin_user,
            cargo='Coordinador'
        )

        # =====================
        # DOCENTES (2)
        # =====================
        docentes = []
        for i in range(1, 3):
            u = Usuario.objects.create(
                nombre=f'Docente {i}',
                email=f'docente{i}@mail.com',
                contraseña='123456',
                estado=True
            )
            d = docente.objects.create(
                usuario=u,
                especialidad=f'Área {i}'
            )
            docentes.append(d)

        # =====================
        # CURSOS (2)
        # =====================
        cursos = []
        for i in range(2):
            c = Curso.objects.create(
                nom=f'Curso {i+1}',
                jornada='Mañana',
                codigo=f'C-00{i+1}',
                capacidad=30,
                docenteid=docentes[i]
            )
            cursos.append(c)

        # =====================
        # ESTUDIANTES (5)
        # =====================
        estudiantes = []
        for i in range(1, 6):
            u = Usuario.objects.create(
                nombre=f'Estudiante {i}',
                email=f'estudiante{i}@mail.com',
                contraseña='123456',
                estado=True
            )
            e = Estudiante.objects.create(
                usuario=u,
                codigo=f'EST-00{i}',
                fechaNacimiento=date(2005, 1, i),
                estadoMatricula='Matriculado',
                fechaIngreso=date.today(),
                cursoId=cursos[i % 2]
            )
            estudiantes.append(e)

        # =====================
        # ACUDIENTES (5)
        # =====================
        acudientes = []
        for i in range(1, 6):
            u = Usuario.objects.create(
                nombre=f'Acudiente {i}',
                email=f'acudiente{i}@mail.com',
                contraseña='123456',
                estado=True
            )
            a = Acudiente.objects.create(
                usuario=u,
                telefono='3000000000',
                direccion=f'Dirección {i}'
            )
            acudientes.append(a)

        # =====================
        # RELACIÓN ESTUDIANTE–ACUDIENTE
        # =====================
        for i in range(5):
            Estudianteacudiente.objects.create(
                estudianteId=estudiantes[i],
                acudienteId=acudientes[i]
            )

        # =====================
        # INVENTARIO
        # =====================
        cat = categoria.objects.create(nombre='Tecnología')
        tipo = tipoelemento.objects.create(nombre='Equipo')
        mar = marca.objects.create(nombre='Lenovo')
        unidad = UnidadMedida.objects.create(nombre='Unidad')

        elemento = Elemento.objects.create(
            nombre='Computador',
            descripcion='Equipo de laboratorio',
            stockActual=20,
            stockMinimo=5,
            tipoElementoId=tipo,
            categoriaId=cat,
            marcaId=mar,
            unidadMedidaId=unidad,
            ubicacion='Laboratorio'
        )

        # =====================
        # MOVIMIENTO
        # =====================
        Movimiento.objects.create(
            tipo='Salida',
            fecha=timezone.now(),
            cantidad=2,
            elementoId=elemento,
            usuarioId=admin_user,
            cursoId=cursos[0],
            motivo='Uso académico'
        )

        # =====================
        # EVENTO + NOTIFICACIÓN
        # =====================
        evento = Evento.objects.create(
            titulo='Evento Institucional',
            descripcion='Actividad general',
            fecha_inicio=timezone.now(),
            fecha_fin=timezone.now(),
            creador_por=admin
        )

        Notificacion.objects.create(
            titulo='Nuevo Evento',
            mensaje='Revisa el evento programado',
            tipo='Evento',
            receptor=admin_user,
            evento=evento
        )

        self.stdout.write(self.style.SUCCESS('✔ Base de datos limpiada y cargada con 10 datos'))
