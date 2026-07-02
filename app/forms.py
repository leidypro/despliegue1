
from django.urls import reverse_lazy
from django import forms
from django.utils import timezone
from app.models import (
    Curso,
    categoria,
    Elemento,
    marca,
    tipoelemento,
    UnidadMedida,
    Movimiento,
    Evento,
    Asistencia,
    Usuario,
    Administrador, Acudiente,
    Estudiante,
    docente,
    Notificacion
)
import re
from django.utils import timezone
from datetime import time

# CURSO


# ── Helper de validación

def solo_letras(value, campo="Este campo"):
    """Solo letras (incluye tildes, ñ y espacios). Sin números ni especiales."""
    value = value.strip()
    if not value:
        raise forms.ValidationError(f"{campo} es obligatorio.")
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", value):
        raise forms.ValidationError(
            f"{campo} solo puede contener letras y espacios, sin números ni caracteres especiales."
        )
    return value


# ── Formulario de Cursos

class CursoForm(forms.ModelForm):

    class Meta:
        model = Curso
        fields = '__all__'
        widgets = {
            'grado': forms.Select(attrs={'class': 'form-control'}),
            'codigo': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'docenteid': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_nom(self):
        return solo_letras(self.cleaned_data.get('nom', ''), "El nombre del curso")

    def clean_jornada(self):
        return solo_letras(self.cleaned_data.get('jornada', ''), "La jornada")

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad <= 0:
            raise forms.ValidationError(
                "La capacidad debe ser un número positivo.")
        return capacidad


class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = '__all__'
        widgets = {
            # Corregido: Quité el guion si tu modelo usa 'estudianteid'
            'estudianteid': forms.Select(attrs={'class': 'form-control'}),
            'horaentrada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horasalida': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.HiddenInput(attrs={
                'class': 'form-control',
                'value': 'Pendiente'  
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].required = False

    def clean_observaciones(self):
        obs = self.cleaned_data.get('observaciones')
        if obs:
            if len(obs) > 200:
                raise forms.ValidationError("Máximo 200 caracteres.")
            if len(obs) < 10:
                raise forms.ValidationError("Mínimo 10 caracteres.")
        return obs

    def clean(self):
        cleaned_data = super().clean()
        estudiante = cleaned_data.get('estudianteid')
        horaentrada = cleaned_data.get('horaentrada')
        horasalida = cleaned_data.get('horasalida')

        # 1. Validación de duplicados por día
        if estudiante:
            fecha_hoy = timezone.now().date()
            existe = Asistencia.objects.filter(
                estudianteid=estudiante,
                fecha__date=fecha_hoy
            ).exclude(pk=self.instance.pk).exists()

            if existe:
                self.add_error(
                    'estudianteid', 'Este estudiante ya tiene asistencia hoy.')

        # 2. Lógica de Estado (A tiempo / Tarde)
        if horaentrada:
            limite = time(7, 0)
            cleaned_data['estado'] = 'A tiempo' if horaentrada <= limite else 'Tarde'

        # 3. Validación de horas
        if horaentrada and horasalida:
            if horaentrada >= horasalida:
                self.add_error(
                    'horasalida', 'La hora de salida debe ser posterior a la de entrada.')

        return cleaned_data
# ── Formulario para Crear Usuario ────────────────────────────────────────────


class UsuarioForm(forms.ModelForm):
    class Meta:

        model = Usuario
        fields = ['nombre', 'email', 'password', 'estado','img_usuario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña', 'id': 'id_contraseña'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'img_usuario': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario

    # Nombre: solo letras

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        return solo_letras(nombre, "El nombre")

    #  Email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email

        email = email.lower()

        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.fields['email'].widget.attrs['class'] = 'form-control is-invalid'
            raise forms.ValidationError(
                "Este correo ya se encuentra registrado. Intenta con uno diferente."
            )

        dominios_permitidos = ['gmail.com',
                               'hotmail.com', 'outlook.com', 'yahoo.com']
        partes = email.split('@')
        if len(partes) > 1 and partes[1] not in dominios_permitidos:
            self.fields['email'].widget.attrs['class'] = 'form-control is-invalid'
            raise forms.ValidationError(
                f"Solo se permiten correos de: {', '.join(dominios_permitidos)}"
            )

        return email

    #  Contraseña

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return password

        errores = []
        if len(password) < 8:
            errores.append("al menos 8 caracteres")
        if not any(c.isupper() for c in password):
            errores.append("una mayúscula")
        if not any(c.isdigit() for c in password):
            errores.append("un número")

        if errores:
            raise forms.ValidationError(f"Falta: {', '.join(errores)}.")

        return password

    #  Confirmar contraseña
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = self.data.get('confirmar_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('password', "Las contraseñas no coinciden.")
        return cleaned_data

#  Formulario para Editar Usuario


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email':  forms.EmailInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        return solo_letras(nombre, "El nombre")


# Formularios de Roles

class AdministradorForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ['cargo']
        widgets = {
            'cargo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Cargo'
            })
        }

    def clean_cargo(self):
        return solo_letras(
            self.cleaned_data.get('cargo', ''), "El cargo"
        )


class DocenteForm(forms.ModelForm):
    class Meta:
        model = docente
        fields = ['especialidad']
        widgets = {
            'especialidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean_especialidad(self):

        return solo_letras(
            self.cleaned_data.get('especialidad', ''), "La especialidad"
        )


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['fechaNacimiento',
                  'estadoMatricula', 'fechaIngreso', 'cursoId']
        widgets = {
            'fechaNacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estadoMatricula': forms.Select(attrs={'class': 'form-control'}),
            'fechaIngreso':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cursoId':         forms.Select(attrs={'class': 'form-control'}),
        }


class AcudienteForm(forms.ModelForm):
    class Meta:
        model = Acudiente
        fields = ['telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }

        def clean(self):
            cleaned_data = super().clean()
            inicio = cleaned_data.get('fecha_inicio')
            fin = cleaned_data.get('fecha_fin')

            if inicio and fin and fin <= inicio:
                self.add_error(
                    'fecha_fin',
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )

            return cleaned_data

        def clean_telefono(self):
            telefono = self.cleaned_data.get('telefono', '')
            if not re.match(r'^\d{7,10}$', telefono):
                raise forms.ValidationError(
                    "El teléfono debe contener solo dígitos (7 a 10 cifras)."
                )
            return telefono

        def clean_direccion(self):
            # Sin restricciones: acepta letras, números y caracteres especiales
            return self.cleaned_data.get('direccion', '')


class TipoElementoForm(forms.ModelForm):
    class Meta:
        model = tipoelemento
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$"
        exist = tipoelemento.objects.filter(
            nombre=nombre).exclude(pk=self.instance.pk).exists()
        if exist:
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "Este Tipo De Elemento ya se encuentra Registrado")
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El Nombre No es Valido (No se usan caracteres especiales ni numeros)")
        return nombre


class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        exist = UnidadMedida.objects.filter(
            nombre=nombre).exclude(pk=self.instance.pk).exists()
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$"
        if exist:
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "Esta Unidad de Medida ya se encuentra Registrado")
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El Nombre No es Valido (No se usan caracteres especiales ni numeros)")
        if not len(nombre) <= 4 and len(nombre) >= 1:
            raise forms.ValidationError(
                "El Nombre de la Unidad debe ser una abreviacion de maximo 4 caracteres")
        return nombre


class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),

            # Campos con botones de creación rápida (CORRECTO)
            'marcaId': forms.Select(attrs={
                'class': 'form-control',
                'data-crear-url': reverse_lazy('app:crear_marca'),
                'data-label': 'Marca'
            }),
            'tipoElementoId': forms.Select(attrs={
                'class': 'form-control',
                'data-crear-url': reverse_lazy('app:crear_tipo'),
                'data-label': 'Tipo de Elemento'
            }),
            'unidadMedidaId': forms.Select(attrs={
                'class': 'form-control',
                'data-crear-url': reverse_lazy('app:crear_unidad'),
                'data-label': 'Unidad de Medida'
            }),
            'categoriaId': forms.Select(attrs={
                'class': 'form-control',
                'data-crear-url': reverse_lazy('app:crear_categoria'),
                'data-label': 'Categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            'stockActual': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'stockMinimo': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control'
            })

        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        exist = Elemento.objects.filter(nombre=nombre).exclude(
            pk=self.instance.pk).exists()
        patron = r"^[A-Za-z 0-9 ÁÉÍÓÚáéíóúÑñ ]+$"
        if exist:
            print('aqui')
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "Este Elemento ya se encuentra Registrado")
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El Nombre No es Valido (No se usan caracteres especiales ni numeros)")
        return nombre

    def clean_stockActual(self):
        stock = self.cleaned_data.get("stockActual")
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo ")
        if not stock.is_integer():
            raise forms.ValidationError("El stock no puede ser decimal ")
        return stock

    def clean_stockMinimo(self):
        stock = self.cleaned_data.get("stockMinimo")
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo ")
        if not stock.is_integer():
            raise forms.ValidationError("El stock no puede ser decimal ")
        return stock

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get('ubicacion', '').strip()
        ubicacion = re.sub(r'\s+', ' ', ubicacion)

        if len(ubicacion) < 3:
            raise forms.ValidationError(
                "La ubicación debe tener al menos 3 caracteres."
            )

        patron = r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-]+$'
        if not re.match(patron, ubicacion):
            raise forms.ValidationError(
                "La ubicación solo puede contener letras, números y guiones."
            )

        return ubicacion


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'docenteid': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',

            }),
        }

    def clean_motivo(self):
        motivo = self.cleaned_data.get('motivo')

        motivo = motivo.strip()

        if len(motivo) < 10 or len(motivo) > 200:
            raise forms.ValidationError(
                "El motivo debe tener entre 10 y 200 caracteres.")

        return motivo


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')

        if Evento.objects.filter(titulo__iexact=titulo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un evento con este título.")

        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")

        if len(descripcion) > 200:
            raise forms.ValidationError(
                "La descripción no puede superar los 200 caracteres.")

        if len(descripcion) < 10:
            raise forms.ValidationError(
                "La descripción debe tener mínimo 10 caracteres.")

        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error(
                    'fecha_fin', "La fecha de fin debe ser mayor que la fecha de inicio.")

        return cleaned_data

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')

        # Validación 1: No permitir que sea solo números
        if titulo.isdigit():
            raise forms.ValidationError(
                "El título no puede contener solo números.")

        # Validación 2: No permitir caracteres especiales
        if not re.match(r'^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9 ]+$', titulo):
            raise forms.ValidationError(
                "El título no puede contener caracteres especiales.")

        return titulo
    # Validación personalizada para el campo capacidad

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')

        if Evento.objects.filter(titulo__iexact=titulo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un evento con este título.")

        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")

        if len(descripcion) > 200:
            raise forms.ValidationError(
                "La descripción no puede superar los 200 caracteres.")

        if len(descripcion) < 10:
            raise forms.ValidationError(
                "La descripción debe tener mínimo 10 caracteres.")

        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error(
                    'fecha_fin', "La fecha de fin debe ser mayor que la fecha de inicio.")

        return cleaned_data


class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'mensaje': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'fecha_envio': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'receptor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'evento': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje')

        if not mensaje:
            raise forms.ValidationError("El mensaje es obligatorio.")

        if len(mensaje) > 200:
            raise forms.ValidationError(
                "El mensaje no puede superar los 200 caracteres.")

        if len(mensaje) < 10:
            raise forms.ValidationError(
                "El mensaje debe tener mínimo 10 caracteres.")

        return mensaje

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')

        # Validación 1: No permitir que sea solo números
        if titulo.isdigit():
            raise forms.ValidationError(
                "El título no puede contener solo números.")

        # Validación 2: No permitir caracteres especiales
        if not re.match(r'^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9 ]+$', titulo):
            raise forms.ValidationError(
                "El título no puede contener caracteres especiales.")

        return titulo
# MARCA


class MarcaForm(forms.ModelForm):
    class Meta:
        model = marca
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        nombre = re.sub(r'\s+', ' ', nombre)

        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )

        patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$'
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El nombre solo puede contener letras y espacios."
            )

        if marca.objects.filter(
            nombre__iexact=nombre
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Ya existe una marca con este nombre."
            )

        return nombre

# CATEGORIA


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        nombre = re.sub(r'\s+', ' ', nombre)

        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )

        patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$'
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El nombre solo puede contener letras y espacios."
            )

        if categoria.objects.filter(
            nombre__iexact=nombre
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Ya existe una categoría con este nombre."
            )

        return nombre

# ELEMENTO


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')

        if Evento.objects.filter(titulo__iexact=titulo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un evento con este título.")

        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")

        if len(descripcion) > 200:
            raise forms.ValidationError(
                "La descripción no puede superar los 200 caracteres.")

        if len(descripcion) < 10:
            raise forms.ValidationError(
                "La descripción debe tener mínimo 10 caracteres.")

        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error(
                    'fecha_fin', "La fecha de fin debe ser mayor que la fecha de inicio.")

        return cleaned_data

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')

        # Validación 1: No permitir que sea solo números
        if titulo.isdigit():
            raise forms.ValidationError(
                "El título no puede contener solo números.")

        # Validación 2: No permitir caracteres especiales
        if not re.match(r'^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9 ]+$', titulo):
            raise forms.ValidationError(
                "El título no puede contener caracteres especiales.")

        return titulo

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio')

        if fecha_inicio and fecha_inicio < timezone.now():
            raise forms.ValidationError(
                "La fecha de inicio no puede ser una fecha pasada."
            )

        return fecha_inicio

    def clean_fecha_fin(self):
        fecha_fin = self.cleaned_data.get('fecha_fin')

        if fecha_fin and fecha_fin < timezone.now():
            raise forms.ValidationError(
                "La fecha de fin no puede ser una fecha pasada."
            )

        return fecha_fin
