from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import ConfiguracionNotificacion, Escuela, Evento, Facultad, Inscripcion, Usuario


# ---------------------------------------------------------------------------
# Resources (definen cómo se mapean los campos para import/export)
# ---------------------------------------------------------------------------

class FacultadResource(resources.ModelResource):
    class Meta:
        model = Facultad
        fields = ("id", "nombre")
        export_order = ("id", "nombre")
        import_id_fields = ("nombre",)


class EscuelaResource(resources.ModelResource):
    facultad = fields.Field(
        column_name="facultad",
        attribute="facultad",
        widget=ForeignKeyWidget(Facultad, field="nombre"),
    )

    class Meta:
        model = Escuela
        fields = ("id", "nombre", "facultad")
        export_order = ("id", "nombre", "facultad")
        import_id_fields = ("nombre",)


class UsuarioResource(resources.ModelResource):
    escuela = fields.Field(
        column_name="escuela",
        attribute="escuela",
        widget=ForeignKeyWidget(Escuela, field="nombre"),
    )

    class Meta:
        model = Usuario
        fields = (
            "id", "username", "first_name", "last_name", "email",
            "rol", "escuela", "cuatrimestre_actual", "is_active",
        )
        export_order = (
            "id", "username", "first_name", "last_name", "email",
            "rol", "escuela", "cuatrimestre_actual", "is_active",
        )
        import_id_fields = ("username",)
        skip_unchanged = True


class EventoResource(resources.ModelResource):
    escuela = fields.Field(
        column_name="escuela",
        attribute="escuela",
        widget=ForeignKeyWidget(Escuela, field="nombre"),
    )
    publicado_por = fields.Field(
        column_name="publicado_por",
        attribute="publicado_por",
        widget=ForeignKeyWidget(Usuario, field="username"),
    )

    class Meta:
        model = Evento
        fields = (
            "id", "titulo", "tipo", "descripcion",
            "fecha_evento", "fecha_fin", "lugar",
            "escuela", "cupo_maximo",
            "cuatrimestre_min", "cuatrimestre_max",
            "publicado_por", "fecha_creacion",
        )
        export_order = (
            "id", "titulo", "tipo", "fecha_evento", "fecha_fin",
            "lugar", "escuela", "cupo_maximo", "publicado_por",
        )
        import_id_fields = ("titulo", "fecha_evento")
        skip_unchanged = True


class InscripcionResource(resources.ModelResource):
    usuario = fields.Field(
        column_name="usuario",
        attribute="usuario",
        widget=ForeignKeyWidget(Usuario, field="username"),
    )
    evento = fields.Field(
        column_name="evento",
        attribute="evento",
        widget=ForeignKeyWidget(Evento, field="titulo"),
    )

    class Meta:
        model = Inscripcion
        fields = ("id", "usuario", "evento", "fecha_registro", "recordatorio_enviado")
        export_order = ("id", "usuario", "evento", "fecha_registro", "recordatorio_enviado")
        import_id_fields = ("usuario", "evento")
        skip_unchanged = True


# ---------------------------------------------------------------------------
# ModelAdmin con Import/Export
# ---------------------------------------------------------------------------

@admin.register(Facultad)
class FacultadAdmin(ImportExportModelAdmin):
    resource_classes = [FacultadResource]
    list_display = ["nombre"]
    search_fields = ["nombre"]


@admin.register(Escuela)
class EscuelaAdmin(ImportExportModelAdmin):
    resource_classes = [EscuelaResource]
    list_display = ["nombre", "facultad"]
    list_filter = ["facultad"]
    search_fields = ["nombre"]


@admin.register(Usuario)
class UsuarioAdmin(ImportExportModelAdmin, UserAdmin):
    resource_classes = [UsuarioResource]
    list_display = ["username", "get_full_name", "email", "rol", "escuela", "cuatrimestre_actual", "is_active"]
    list_filter = ["rol", "escuela__facultad", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Perfil UNPHU",
            {"fields": ("rol", "escuela", "cuatrimestre_actual")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Perfil UNPHU",
            {"fields": ("rol", "escuela", "cuatrimestre_actual")},
        ),
    )


@admin.register(Evento)
class EventoAdmin(ImportExportModelAdmin):
    resource_classes = [EventoResource]
    list_display = [
        "titulo",
        "tipo",
        "fecha_evento",
        "fecha_fin",
        "escuela",
        "lugar",
        "publicado_por",
        "cupo_maximo",
        "cupos_disponibles_display",
        "fecha_creacion",
    ]
    list_filter = ["tipo", "escuela", "escuela__facultad"]
    search_fields = ["titulo", "descripcion", "lugar"]
    readonly_fields = ["publicado_por", "fecha_creacion", "fecha_modificacion"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.publicado_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Cupos disponibles")
    def cupos_disponibles_display(self, obj):
        disp = obj.cupos_disponibles()
        return "∞" if disp is None else disp


@admin.register(Inscripcion)
class InscripcionAdmin(ImportExportModelAdmin):
    resource_classes = [InscripcionResource]
    list_display = ["usuario", "evento", "fecha_registro", "recordatorio_enviado"]
    list_filter = ["recordatorio_enviado", "evento__tipo"]
    search_fields = ["usuario__username", "evento__titulo"]
    readonly_fields = ["fecha_registro"]


@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = [
        "usuario",
        "confirmacion_inscripcion",
        "recordatorio_evento",
        "horas_recordatorio",
        "notificar_nueva_actividad_escuela",
        "notificar_nueva_actividad_facultad",
    ]
    list_filter = ["confirmacion_inscripcion", "recordatorio_evento"]
