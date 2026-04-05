from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Usuario, Evento, ConfiguracionNotificacion, Escuela


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, label="Nombre", widget=forms.TextInput(attrs={"placeholder": "Nombre"})
    )
    last_name = forms.CharField(
        max_length=150, label="Apellido", widget=forms.TextInput(attrs={"placeholder": "Apellido"})
    )
    email = forms.EmailField(
        required=True, label="Correo electrónico", widget=forms.EmailInput(attrs={"placeholder": "correo@unphu.edu.do"})
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "escuela",
            "cuatrimestre_actual",
            "password1",
            "password2",
        ]
        labels = {
            "username": "Nombre de usuario",
            "escuela": "Escuela / Carrera",
            "cuatrimestre_actual": "Cuatrimestre actual",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "nombre.apellido"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["escuela"].queryset = Escuela.objects.select_related("facultad").order_by(
            "nombre"
        )
        self.fields["escuela"].required = False
        self.fields["cuatrimestre_actual"].required = False
        self.fields["cuatrimestre_actual"].widget.attrs["min"] = 1
        self.fields["cuatrimestre_actual"].widget.attrs["max"] = 10
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "")


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "escuela", "cuatrimestre_actual"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "escuela": "Escuela / Carrera",
            "cuatrimestre_actual": "Cuatrimestre actual",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["escuela"].queryset = Escuela.objects.select_related("facultad").order_by(
            "nombre"
        )
        self.fields["escuela"].required = False
        self.fields["cuatrimestre_actual"].required = False
        self.fields["cuatrimestre_actual"].widget.attrs.update({"min": 1, "max": 10})
        self.fields["email"].required = True


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            "titulo",
            "tipo",
            "descripcion",
            "fecha_evento",
            "fecha_fin",
            "lugar",
            "escuela",
            "cupo_maximo",
            "enlace_virtual",
            "defensor",
            "jurados",
            "cuatrimestre_min",
            "cuatrimestre_max",
            "imagen",
        ]
        labels = {
            "titulo": "Título",
            "tipo": "Tipo de evento",
            "descripcion": "Descripción",
            "fecha_evento": "Fecha y hora de inicio",
            "fecha_fin": "Fecha y hora de finalización",
            "lugar": "Lugar / Edificio",
            "escuela": "Escuela organizadora",
            "cupo_maximo": "Cupo máximo (0 = sin límite)",
            "enlace_virtual": "Enlace de reunión virtual",
            "defensor": "Estudiante defensor",
            "jurados": "Jurado",
            "cuatrimestre_min": "Cuatrimestre mínimo relevante",
            "cuatrimestre_max": "Cuatrimestre máximo relevante",
            "imagen": "Imagen del evento",
        }
        widgets = {
            "fecha_evento": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "fecha_fin": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "descripcion": forms.Textarea(attrs={"rows": 5}),
            "jurados": forms.Textarea(attrs={"rows": 4, "placeholder": "Ej.\nDr. Carlos Méndez\nIng. Rosa Belén Castillo\nIng. José Rodríguez", "class": "w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-unphu resize-y"}),
            "cuatrimestre_min": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "cuatrimestre_max": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["escuela"].queryset = Escuela.objects.select_related("facultad").order_by(
            "nombre"
        )
        self.fields["enlace_virtual"].required = False
        self.fields["defensor"].required = False
        self.fields["jurados"].required = False
        self.fields["cuatrimestre_min"].required = False
        self.fields["cuatrimestre_max"].required = False
        self.fields["fecha_fin"].required = False
        self.fields["imagen"].required = False
        # Pre-populate datetime widgets correctly
        if self.instance and self.instance.pk:
            if self.instance.fecha_evento:
                self.initial["fecha_evento"] = self.instance.fecha_evento.strftime(
                    "%Y-%m-%dT%H:%M"
                )
            if self.instance.fecha_fin:
                self.initial["fecha_fin"] = self.instance.fecha_fin.strftime(
                    "%Y-%m-%dT%H:%M"
                )

    def clean(self):
        cleaned = super().clean()
        fecha_inicio = cleaned.get("fecha_evento")
        fecha_fin = cleaned.get("fecha_fin")
        sem_min = cleaned.get("cuatrimestre_min")
        sem_max = cleaned.get("cuatrimestre_max")

        if fecha_inicio and fecha_inicio <= timezone.now():
            self.add_error("fecha_evento", "La fecha de inicio debe ser en el futuro.")

        if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
            self.add_error(
                "fecha_fin",
                "La fecha de finalización debe ser posterior a la fecha de inicio.",
            )

        if sem_min and sem_max and sem_min > sem_max:
            self.add_error(
                "cuatrimestre_max",
                "El cuatrimestre máximo debe ser mayor o igual al cuatrimestre mínimo.",
            )

        if cleaned.get("tipo") == "TESIS":
            if not cleaned.get("defensor"):
                self.add_error("defensor", "El nombre del defensor es obligatorio para presentaciones de tesis.")
            if not cleaned.get("jurados"):
                self.add_error("jurados", "El jurado es obligatorio para presentaciones de tesis.")

        return cleaned


class ConfiguracionNotificacionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionNotificacion
        fields = [
            "confirmacion_inscripcion",
            "recordatorio_evento",
            "dias_recordatorio",
            "notificar_nueva_actividad_escuela",
            "notificar_nueva_actividad_facultad",
        ]
        labels = {
            "confirmacion_inscripcion": "Confirmación de inscripción",
            "recordatorio_evento": "Recordatorio antes del evento",
            "dias_recordatorio": "Días de anticipación para el recordatorio",
            "notificar_nueva_actividad_escuela": "Notificarme cuando haya nuevos eventos en mi escuela",
            "notificar_nueva_actividad_facultad": "Notificarme cuando haya nuevos eventos en mi facultad",
        }
        widgets = {
            "dias_recordatorio": forms.NumberInput(attrs={"min": 1, "max": 30}),
        }

    def clean_dias_recordatorio(self):
        dias = self.cleaned_data.get("dias_recordatorio")
        if dias is not None and dias < 1:
            raise forms.ValidationError("Debe ser al menos 1 día.")
        return dias
