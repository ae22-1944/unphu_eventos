from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sistema", "0003_rename_semestre_to_cuatrimestre"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="enlace_virtual",
            field=models.URLField(
                blank=True,
                verbose_name="Enlace de reunión virtual",
                help_text="URL de Zoom, Google Meet, Teams, etc. (opcional)",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="defensor",
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name="Estudiante defensor",
                help_text="Solo para presentaciones de tesis",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="jurados",
            field=models.TextField(
                blank=True,
                verbose_name="Jurado",
                help_text="Un nombre por línea. Solo para presentaciones de tesis.",
            ),
        ),
    ]
