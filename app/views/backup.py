import os
import subprocess
import platform
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

# ========== OBTENER DATOS DE LA BD (MULTIPLATAFORMA) ==========
def obtener_credenciales_mysql():
    """Detecta el SO y ajusta las rutas de los binarios de MySQL automáticamente"""
    db_config = settings.DATABASES['default']
    sistema = platform.system()
    
    creds = {
        'host': db_config.get('HOST', 'localhost'),
        'user': db_config.get('USER', 'root'),
        'password': db_config.get('PASSWORD', ''),
        'database': db_config.get('NAME', 'colegio_db'),
        'port': db_config.get('PORT', 3306),
    }

    if sistema == "Windows":
        # Rutas comunes en Windows (MySQL oficial o XAMPP)
        rutas_posibles = [
            r'C:\Program Files\MySQL\MySQL Server 8.0\bin',
            r'C:\xampp\mysql\bin',
            r'C:\Program Files\MySQL\MySQL Server 8.4\bin'
        ]
        creds['mysql_path'] = next((r for r in rutas_posibles if os.path.exists(r)), rutas_posibles[0])
        creds['ext'] = '.exe'
    else:
        # En Linux (Pop!_OS/Ubuntu) los binarios están en el PATH global
        creds['mysql_path'] = '/usr/bin'
        creds['ext'] = ''
        
    return creds

def probar_conexion_mysql():
    """Prueba la conexión a MySQL ejecutando un comando simple"""
    creds = obtener_credenciales_mysql()
    try:
        # Usamos f-string para la extensión (.exe o vacío)
        exe = f"mysql{creds['ext']}"
        cmd = [
            os.path.join(creds["mysql_path"], exe),
            '-h', creds["host"],
            '-u', creds["user"],
            '-P', str(creds["port"]),
            f'--password={creds["password"]}',
            '-e', 'SELECT 1;',
            creds["database"]
        ]

        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return resultado.returncode == 0
    except:
        return False

# ========== VISTA PRINCIPAL DEL BACKUP ==========
@require_http_methods(["GET", "POST"])
def backup(request):
    """Muestra el menú de opciones para respaldo y restauración"""
    if request.method == "POST":
        accion = request.POST.get('accion')
        try:
            if accion == 'backup_completo':
                if not probar_conexion_mysql():
                    return JsonResponse({'error': 'Error de conexión. Verifica el servidor MySQL.'}, status=400)
                return realizar_respaldo_completo()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    context = {
        'titulo': 'Gestión de Base de Datos - ProyectoColegio',
        'mysql_conectado': probar_conexion_mysql(),
    }
    return render(request, 'backup/menu.html', context)

# ========== FUNCIONES DE RESPALDO ==========
def realizar_respaldo_completo():
    """Genera el volcado SQL (Estructura + Datos)"""
    creds = obtener_credenciales_mysql()
    try:
        exe = f"mysqldump{creds['ext']}"
        cmd = [
            os.path.join(creds["mysql_path"], exe),
            '-h', creds["host"],
            '-u', creds["user"],
            '-P', str(creds["port"]),
            f'--password={creds["password"]}',
            '--routines', '--triggers', '--events',
            creds["database"]
        ]

        resultado = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=60)

        if resultado.returncode != 0:
            raise Exception(f"Error en mysqldump: {resultado.stderr}")

        header = f"-- Respaldo ProyectoColegio\n-- Fecha: {datetime.now()}\n\n"
        return generar_archivo_descarga(header + resultado.stdout, 'respaldo_colegio')

    except Exception as e:
        raise Exception(f"Fallo al generar backup: {str(e)}")

# ========== FUNCIONES DE RESTAURACIÓN ==========
@require_http_methods(["POST"])
def restaurar_datos(request):
    """Recibe un archivo .sql y lo inyecta en la BD con validación de contenido"""
    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No hay archivo seleccionado'}, status=400)

    archivo = request.FILES['archivo']
    
    # 1. Validar extensión
    if not archivo.name.endswith('.sql'):
        return JsonResponse({'error': 'Formato no válido. Debe ser un archivo .sql'}, status=400)

    # 2. Validar que el archivo NO esté vacío (0 bytes)
    if archivo.size == 0:
        return JsonResponse({'error': 'El archivo está vacío'}, status=400)

    try:
        # Leer el contenido
        contenido_sql = archivo.read().decode('utf-8')

        # 3. Validar que no sean solo espacios o saltos de línea
        if not contenido_sql.strip():
            return JsonResponse({'error': 'El archivo no contiene comandos SQL válidos'}, status=400)

        creds = obtener_credenciales_mysql()
        exe = f"mysql{creds['ext']}"
        
        cmd = [
            os.path.join(creds["mysql_path"], exe),
            '-h', creds["host"],
            '-u', creds["user"],
            '-P', str(creds["port"]),
            f'--password={creds["password"]}',
            creds["database"]
        ]

        proceso = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Aquí le pasamos el contenido que acabamos de validar
        stdout, stderr = proceso.communicate(input=contenido_sql, timeout=120)

        if proceso.returncode != 0:
            raise Exception(stderr)

        return JsonResponse({'exito': True, 'mensaje': 'Base de datos restaurada con éxito'})
    
    except UnicodeDecodeError:
        return JsonResponse({'error': 'El archivo tiene un formato de texto incompatible (usa UTF-8)'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=400)
def generar_archivo_descarga(contenido, nombre):
    """Crea la respuesta HTTP para descargar el SQL"""
    response = HttpResponse(contenido.encode('utf-8'), content_type='application/sql')
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{nombre}_{fecha}.sql"'
    return response