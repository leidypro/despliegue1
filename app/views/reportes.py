from django.shortcuts import render, redirect
from django.views.generic import View
from django.views import View as DjangoView
from django.http import HttpResponse
from app.models import *
from django.db.models import Q
from app.utils import exportar_pdf, exportar_excel
from datetime import datetime
from django.contrib import messages
# ====== VISTAS PARA EXPORTAR REPORTES ======


class ExportarUsuarioPDF(DjangoView):

    def get(self, request):
        print("Aqui")

        usuarios = Usuario.objects.all()
        if not usuarios.exists():
            messages.warning(
                request, "No existen usuarios registrados en el sistema.")
            return redirect('app:index_usuario')
        buscar = request.GET.get('buscar', '').strip()
        rol = request.GET.get('rol', '').strip()
        estado = request.GET.get('estado', '').strip()

        # ===== BUSQUEDA =====
        if buscar:
            usuarios = usuarios.filter(
                Q(nombre__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        # ===== ESTADO =====
        if estado in ['0', '1']:
            usuarios = usuarios.filter(estado=estado)

        # ===== ROL =====
        if rol == "administrador":
            usuarios = usuarios.filter(administrador__isnull=False)

        elif rol == "docente":
            usuarios = usuarios.filter(docente__isnull=False)

        elif rol == "estudiante":
            usuarios = usuarios.filter(estudiante__isnull=False)

        # ===== VALIDAR RESULTADOS =====
        if not usuarios.exists():
            messages.warning(request, "No existen usuarios con ese filtro")
            return redirect('app:index_usuario')

        columnas = ['ID', 'Nombre', 'Email', 'Rol', 'Estado']

        datos = [
            (
                us.id,
                us.nombre,
                us.email,
                us.get_rol(),
                "Activo" if us.estado else "Inactivo"
            )
            for us in usuarios
        ]

        nombre_archivo = f'Reporte_Usuarios_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_pdf(
            request,
            titulo='REPORTE DE USUARIOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarUsuarioExcel(DjangoView):
    """
    VISTA PARA EXPORTAR CATEGORIAS A EXCEL
    Obtiene todas las categorias y las exporta en formato Excel
    """

    def get(self, request):
        print("Aqui")

        usuarios = Usuario.objects.all()
        if not usuarios.exists():
            messages.warning(
                request, "No existen usuarios registrados en el sistema.")
            return redirect('app:index_usuario')
        buscar = request.GET.get('buscar', '').strip()
        rol = request.GET.get('rol', '').strip()
        estado = request.GET.get('estado', '').strip()

        # ===== BUSQUEDA =====
        if buscar:
            usuarios = usuarios.filter(
                Q(nombre__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        # ===== ESTADO =====
        if estado in ['0', '1']:
            usuarios = usuarios.filter(estado=estado)

        # ===== ROL =====
        if rol == "administrador":
            usuarios = usuarios.filter(administrador__isnull=False)

        elif rol == "docente":
            usuarios = usuarios.filter(docente__isnull=False)

        elif rol == "estudiante":
            usuarios = usuarios.filter(estudiante__isnull=False)

        # ===== VALIDAR RESULTADOS =====
        if not usuarios.exists():
            messages.warning(request, "No existen usuarios con ese filtro")
            return redirect('app:index_usuario')

        columnas = ['ID', 'Nombre', 'Email', 'Rol', 'Estado']

        datos = [
            (
                us.id,
                us.nombre,
                us.email,
                us.get_rol(),
                "Activo" if us.estado else "Inactivo"
            )
            for us in usuarios
        ]

        nombre_archivo = f'Reporte_Usuarios_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE CATEGORIAS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarAsistenciaPDF(DjangoView):
    """
    VISTA PARA EXPORTAR CATEGORIAS A PDF
    Obtiene todas las categorías y las exporta en formato PDF
    """

    def get(self, request):
        # Obtener todas las categorias
        asistencia = Asistencia.objects.all()
        if not asistencia.exists():
            messages.warning(
                request, "No existen asistencias registrados en el sistema.")
            return redirect('app:index_asistencia')
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'NOMBRE DEL ESTUDIANTE', 'FECHA', 'OBSERVACIONES']

        # Preparar los datos en formato de tuplas
        datos = [
            (asi.id, asi.estudianteid, asi.fecha, asi.observaciones)
            for asi in asistencia
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Asistencias_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_pdf(
            request,
            titulo='REPORTE DE ASISTENCIAS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,

        )


class ExportarAsistenciaExcel(DjangoView):
    """
    VISTA PARA EXPORTAR CATEGORIAS A EXCEL
    Obtiene todas las categorias y las exporta en formato Excel
    """

    def get(self, request):
        # Obtener todas las categorias
        asistencia = Asistencia.objects.all()
        if not asistencia.exists():
            messages.warning(
                request, "No existen asistencias registrados en el sistema.")
            return redirect('app:index_asistencia')
        # Definir las columnas que se mostraran en el reporte
        columnas = ['ID', 'NOMBRE DEL ESTUDIANTE', 'FECHA', 'OBSERVACIONES']

        # Preparar los datos en  tuplas
        datos = [
            (asi.id, asi.estudianteid, asi.fecha, asi.observaciones)
            for asi in asistencia
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Asistencias_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE ASISTENCIA',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarEventosPDF(DjangoView):
    """
    VISTA PARA EXPORTAR CATEGORIAS A PDF
    Obtiene todas las categorías y las exporta en formato PDF
    """

    def get(self, request):
        # Obtener todas las categorias
        evento = Evento.objects.all()
        if not evento.exists():
            messages.warning(
                request, "No existen eventos registrados en el sistema.")
            return redirect('app:index_evento')
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'TITULO', 'DESCRIPCION']

        # Preparar los datos en formato de tuplas
        datos = [
            (us.id, us.titulo, us.descripcion)
            for us in evento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Eventos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_pdf(
            request,
            titulo='REPORTE DE EVENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,

        )


class ExportarEventosExcel(DjangoView):

    def get(self, request):
        # Obtener todas las categorias
        evento = Evento.objects.all()
        if not evento.exists():
            messages.warning(
                request, "No existen eventos registrados en el sistema.")
            return redirect('app:index_evento')
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'TITULO', 'DESCRIPCION']

        # Preparar los datos en formato de tuplas
        datos = [
            (us.id, us.titulo, us.descripcion)
            for us in evento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Eventos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_excel(
            titulo='REPORTE DE EVENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,

        )


class ExportarMovimientosPDF(DjangoView):
    """
    VISTA PARA EXPORTAR Movimientos A PDF
    Obtiene todas los movimientos y los exporta en formato PDF
    """

    def get(self, request):
        # Obtener todas las categorias
        movimiento = Movimiento.objects.all()
        if not movimiento.exists():
            messages.warning(
                request, "No existen movimientos registrados en el sistema.")
            return redirect('app:index_movimiento')
        # Definir las columnas que se muestran en el reporte
        columnas = ["id", "fecha", 'cantidad',
                    "elementoid", "usuarioid", "cursoid"]

        # Preparar los datos en formato de tuplas
        datos = [
            (mo.id, mo.fecha, mo.cantidad, mo.elementoid, mo.usuarioid, mo.cursoid)
            for mo in movimiento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_movimientos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_pdf(
            request,
            titulo='REPORTE DE MOVIMIENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,

        )


class ExportarMovimientosExcel(DjangoView):
    """
    VISTA PARA EXPORTAR MOVIMIENTOS A EXCEL
    Obtiene todos los movimientos y los exporta en formato Excel
    """

    def get(self, request):
        # Obtener todas las categorias
        movimiento = Movimiento.objects.all()
        if not movimiento.exists():
            messages.warning(
                request, "No existen movimientos registrados en el sistema.")
            return redirect('app:index_movimiento')
        # Definir las columnas que se mostraran en el reporte
        columnas = ["id", 'fecha', 'cantidad',
                    "elementoid", "usuarioid", "cursoid"]

        # Preparar los datos en  tuplas
        datos = [
            (mo.id, mo.fecha, mo.cantidad, mo.elementoid, mo.usuarioid, mo.cursoid)
            for mo in movimiento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_movimientos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE MOVIMIENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarInventarioPDF(DjangoView):
    def get(self, request):
        inventario = Elemento.objects.all()
        if not inventario.exists():
            messages.warning(
                request, "No existen inventario registrados en el sistema.")
            return redirect('app:index_inventario')
        columnas = ['ID', 'Nombre', 'Marca', 'Categoría', 'Stock', 'Ubicación']

        datos = [
            (
                inv.id,
                inv.nombre,
                inv.marcaId.nombre,        # FK → marca.nombre
                inv.categoriaId.nombre,    # FK → categoria.nombre
                inv.stockActual,
                inv.ubicacion
            )
            for inv in inventario
        ]

        nombre_archivo = f'Reporte_Inventario_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_pdf(
            request,
            titulo='REPORTE DE INVENTARIO',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,
        )


class ExportarInventarioExcel(DjangoView):
    def get(self, request):
        inventario = Elemento.objects.select_related(
            'marcaId', 'categoriaId').all()
        if not inventario.exists():
            messages.warning(request, "No existen inventario registrados en el sistema.")
            return redirect('app:index_inventario')
        columnas = ['ID', 'Nombre', 'Marca', 'Categoría', 'Stock', 'Ubicación']

        datos = [
            (
                inv.id,
                inv.nombre,
                inv.marcaId.nombre,        # FK → marca.nombre
                inv.categoriaId.nombre,    # FK → categoria.nombre
                inv.stockActual,
                inv.ubicacion
            )
            for inv in inventario
        ]

        nombre_archivo = f'Reporte_Inventario_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_excel(
            titulo='REPORTE DE INVENTARIO',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarCursoPDF(DjangoView):
    def get(self, request):
        # 1. Capturamos el ID que viene del selector del HTML
        curso_id = request.GET.get('curso_id')

        # 2. Si hay un ID, filtramos. Si no, traemos todos.
        if curso_id:
            cursos = Curso.objects.filter(id=curso_id)
            curso_obj = cursos.first()
            grado_nombre = curso_obj.get_grado_display() if curso_obj else curso_id
            titulo_reporte = f'REPORTE DEL CURSO: {grado_nombre}'
        else:
            cursos = Curso.objects.all()
            if not cursos.exists():
                messages.warning(request, "No existen cursos registrados en el sistema.")
                return redirect('app:index_curso')
            titulo_reporte = 'REPORTE GENERAL DE CURSOS'

        columnas = ['ID', 'Grado', 'Código', 'Capacidad']

        # 3. Preparamos los datos usando la variable 'cursos' (ya filtrada)
        datos = [
            (c.id, c.grado, c.codigo, c.capacidad)
            for c in cursos
        ]

        nombre_archivo = f'Reporte_Cursos_{datetime.now().strftime("%d_%m_%Y")}'

        # 4. Retornamos la función que genera el PDF
        return exportar_pdf(
            request,
            titulo=titulo_reporte,
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarCursoExcel(DjangoView):
    def get(self, request):
        # 1. Capturamos el ID que viene del selector del HTML
        curso_id = request.GET.get('curso_id')

        # 2. Si hay un ID, filtramos. Si no, traemos todos.
        if curso_id:
            cursos = Curso.objects.filter(id=curso_id)
            titulo_reporte = f'REPORTE DEL CURSO #{curso_id}'
        else:
            cursos = Curso.objects.all()
            if not cursos.exists():
                messages.warning(request, "No existen cursos registrados en el sistema.")
                return redirect('app:index_curso')
            titulo_reporte = 'REPORTE GENERAL DE CURSOS'

        columnas = ['ID', 'Grado', 'Código', 'Capacidad']

        # Usamos la variable 'cursos' que ya está filtrada arriba
        datos = [
            (c.id, c.grado, c.codigo, c.capacidad)
            for c in cursos
        ]

        nombre_archivo = f'Reporte_Cursos_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_excel(
            titulo=titulo_reporte,
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )
