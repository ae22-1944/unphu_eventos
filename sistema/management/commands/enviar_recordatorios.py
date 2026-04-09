from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from sistema.models import Inscripcion


class Command(BaseCommand):
    help = "Envía recordatorios por correo a usuarios inscritos en eventos próximos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--forzar",
            action="store_true",
            help=(
                "Ignora la ventana de tiempo y envía recordatorio a todos los eventos "
                "futuros en los que el usuario está inscrito. Útil para pruebas y demos."
            ),
        )

    def handle(self, *args, **options):
        forzar = options["forzar"]
        ahora = timezone.now()
        enviados = 0
        errores = 0

        inscripciones = (
            Inscripcion.objects.filter(
                evento__fecha_evento__gt=ahora,
                usuario__configuracion_notificacion__recordatorio_evento=True,
            )
            .select_related(
                "usuario",
                "usuario__configuracion_notificacion",
                "evento",
                "evento__escuela",
            )
        )

        if forzar:
            self.stdout.write(
                self.style.WARNING("Modo --forzar activo: se ignora la ventana de tiempo.")
            )
            # Resetear recordatorio_enviado para poder reenviar durante demos
            inscripciones.update(recordatorio_enviado=False)
        else:
            inscripciones = inscripciones.filter(recordatorio_enviado=False)

        for inscripcion in inscripciones:
            config = inscripcion.usuario.configuracion_notificacion

            if not forzar:
                horas = config.horas_recordatorio
                ventana_inicio = ahora + timedelta(hours=horas) - timedelta(minutes=15)
                ventana_fin = ahora + timedelta(hours=horas) + timedelta(minutes=15)

                if not (ventana_inicio <= inscripcion.evento.fecha_evento <= ventana_fin):
                    continue

            if not inscripcion.usuario.email:
                continue

            try:
                subject = f"Recordatorio: {inscripcion.evento.titulo} es pronto"
                body = render_to_string(
                    "sistema/emails/recordatorio_evento.txt",
                    {
                        "usuario": inscripcion.usuario,
                        "evento": inscripcion.evento,
                        "horas": config.horas_recordatorio,
                    },
                )
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [inscripcion.usuario.email],
                    fail_silently=False,
                )
                inscripcion.recordatorio_enviado = True
                inscripcion.save(update_fields=["recordatorio_enviado"])
                enviados += 1
                self.stdout.write(
                    f"  ✓ Recordatorio enviado a {inscripcion.usuario.email} "
                    f"para «{inscripcion.evento.titulo}»"
                )
            except Exception as e:
                errores += 1
                self.stderr.write(
                    f"  ✗ Error enviando a {inscripcion.usuario.email}: {e}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nResumen: {enviados} recordatorio(s) enviado(s), {errores} error(es)."
            )
        )
