from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Escuela(models.Model):
    nombre = models.CharField(max_length=100)
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.SET_NULL,
        related_name="escuelas",
        null=True,
        blank=True,
        help_text="Opcional — dejar vacío si la escuela no pertenece a una facultad separada",
    )

    class Meta:
        verbose_name = "Escuela"
        verbose_name_plural = "Escuelas"
        ordering = ["nombre"]

    def __str__(self):
        if self.facultad:
            return f"{self.nombre} — {self.facultad.nombre}"
        return self.nombre


class Usuario(AbstractUser):
    ROL_CHOICES = [("ADMIN", "Administrador"), ("ESTUDIANTE", "Estudiante")]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="ESTUDIANTE")
    escuela = models.ForeignKey(
        Escuela, on_delete=models.SET_NULL, null=True, blank=True
    )
    cuatrimestre_actual = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Cuatrimestre actual del estudiante (1–10)",
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    def es_admin(self):
        return self.rol == "ADMIN"


class ConfiguracionNotificacion(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="configuracion_notificacion",
    )
    confirmacion_inscripcion = models.BooleanField(
        default=True,
        verbose_name="Confirmación de inscripción",
        help_text="Recibir correo al inscribirse en un evento",
    )
    recordatorio_evento = models.BooleanField(
        default=True,
        verbose_name="Recordatorio de evento",
        help_text="Recibir recordatorio antes del evento",
    )
    dias_recordatorio = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Días de anticipación",
        help_text="Cuántos días antes del evento recibir el recordatorio",
    )
    notificar_nueva_actividad_escuela = models.BooleanField(
        default=True,
        verbose_name="Nuevos eventos en mi escuela",
        help_text="Recibir correo cuando se publique un nuevo evento en mi escuela",
    )
    notificar_nueva_actividad_facultad = models.BooleanField(
        default=False,
        verbose_name="Nuevos eventos en mi facultad",
        help_text="Recibir correo cuando se publique un nuevo evento en mi facultad",
    )

    class Meta:
        verbose_name = "Configuración de Notificaciones"
        verbose_name_plural = "Configuraciones de Notificaciones"

    def __str__(self):
        return f"Notificaciones de {self.usuario.username}"


class Evento(models.Model):
    TIPO_CHOICES = [
        ("TESIS", "Presentación de Tesis"),
        ("ACADEMICA", "Actividad Académica"),
        ("INSTITUCIONAL", "Evento Institucional"),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    cupo_maximo = models.PositiveIntegerField(
        default=0,
        verbose_name="Cupo máximo",
        help_text="0 = sin límite de cupos",
    )
    fecha_evento = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de finalización",
        help_text="Opcional — si el evento tiene duración definida",
    )
    escuela = models.ForeignKey(
        Escuela, on_delete=models.CASCADE, verbose_name="Escuela"
    )
    lugar = models.CharField(max_length=200, verbose_name="Lugar / Edificio")
    enlace_virtual = models.URLField(
        blank=True,
        verbose_name="Enlace de reunión virtual",
        help_text="URL de Zoom, Google Meet, Teams, etc. (opcional)",
    )
    defensor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Estudiante defensor",
        help_text="Solo para presentaciones de tesis",
    )
    jurados = models.TextField(
        blank=True,
        verbose_name="Jurado",
        help_text="Un nombre por línea. Solo para presentaciones de tesis.",
    )
    imagen = models.ImageField(
        upload_to="eventos/",
        null=True,
        blank=True,
        verbose_name="Imagen del evento",
    )
    publicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_publicados",
        verbose_name="Publicado por",
    )
    cuatrimestre_min = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Cuatrimestre mínimo relevante",
        help_text="Dejar vacío si aplica a todos los cuatrimestres",
    )
    cuatrimestre_max = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Cuatrimestre máximo relevante",
        help_text="Dejar vacío si aplica a todos los cuatrimestres",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["fecha_evento"]

    def __str__(self):
        return self.titulo

    def cupos_disponibles(self):
        if self.cupo_maximo == 0:
            return None  # sin límite
        inscritos = self.inscripcion_set.count()
        return max(0, self.cupo_maximo - inscritos)

    def tiene_cupo(self):
        if self.cupo_maximo == 0:
            return True
        return self.cupos_disponibles() > 0


class Inscripcion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    recordatorio_enviado = models.BooleanField(default=False)

    class Meta:
        unique_together = ("usuario", "evento")
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.usuario.username} → {self.evento.titulo}"
