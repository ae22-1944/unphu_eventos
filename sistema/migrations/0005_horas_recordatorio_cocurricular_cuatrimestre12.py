import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sistema", "0004_evento_enlace_virtual_defensor_jurados"),
    ]

    operations = [
        # Grupo 1: dias_recordatorio → horas_recordatorio
        migrations.RenameField(
            model_name="configuracionnotificacion",
            old_name="dias_recordatorio",
            new_name="horas_recordatorio",
        ),
        # Grupo 2: campo cocurricular en Evento
        migrations.AddField(
            model_name="evento",
            name="es_cocurricular",
            field=models.BooleanField(
                default=False,
                verbose_name="Cuenta como horas cocurriculares",
                help_text="Marcar si este evento otorga horas cocurriculares a los inscritos",
            ),
        ),
        # Grupo 4: cuatrimestre máx 10 → 12
        migrations.AlterField(
            model_name="evento",
            name="cuatrimestre_min",
            field=models.IntegerField(
                null=True,
                blank=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
                verbose_name="Cuatrimestre mínimo relevante",
                help_text="Dejar vacío si aplica a todos los cuatrimestres",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="cuatrimestre_max",
            field=models.IntegerField(
                null=True,
                blank=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
                verbose_name="Cuatrimestre máximo relevante",
                help_text="Dejar vacío si aplica a todos los cuatrimestres",
            ),
        ),
    ]
