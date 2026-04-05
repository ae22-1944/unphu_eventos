from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sistema", "0002_alter_escuela_options_evento_fecha_fin_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="usuario",
            old_name="semestre_actual",
            new_name="cuatrimestre_actual",
        ),
        migrations.RenameField(
            model_name="evento",
            old_name="semestre_min",
            new_name="cuatrimestre_min",
        ),
        migrations.RenameField(
            model_name="evento",
            old_name="semestre_max",
            new_name="cuatrimestre_max",
        ),
    ]
