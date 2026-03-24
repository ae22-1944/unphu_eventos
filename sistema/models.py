from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    ROL_CHOICES = [("ADMIN", "Administrador"), ("ESTUDIANTE", "Estudiante")]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="ESTUDIANTE")
    escuela = models.ForeignKey(
        "Escuela", on_delete=models.SET_NULL, null=True, blank=True
    )


class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Escuela(models.Model):
    nombre = models.CharField(max_length=100)
    facultad = models.ForeignKey(
        Facultad, on_delete=models.CASCADE, related_name="escuelas"
    )

    def __str__(self):
        return f"{self.nombre} ({self.facultad.nombre})"


class Evento(models.Model):
    TIPO_CHOICES = [
        ("TESIS", "Tesis"),
        ("CHARLA", "Charla"),
        ("AVISO", "Aviso Oficial"),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cupo_maximo = models.PositiveIntegerField(default=0)
    fecha_evento = models.DateTimeField()
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo


class Inscripcion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "evento")
