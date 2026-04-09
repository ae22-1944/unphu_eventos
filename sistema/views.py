from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ConfiguracionNotificacionForm,
    EventoForm,
    PerfilForm,
    RegistroForm,
)
from .models import (
    ConfiguracionNotificacion,
    Escuela,
    Evento,
    Facultad,
    Inscripcion,
)


# ---------------------------------------------------------------------------
# Decoradores
# ---------------------------------------------------------------------------

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as django_settings
            return redirect(f"{django_settings.LOGIN_URL}?next={request.path}")
        if request.user.rol != "ADMIN":
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _calcular_prioridad(evento, usuario):
    score = 0
    if usuario.escuela_id and evento.escuela_id == usuario.escuela_id:
        score += 3
    elif (
        usuario.escuela_id
        and evento.escuela.facultad_id == usuario.escuela.facultad_id
    ):
        score += 2
    if (
        evento.tipo == "TESIS"
        and usuario.cuatrimestre_actual
        and usuario.cuatrimestre_actual >= 7
    ):
        score += 2
    if (
        evento.cuatrimestre_min is not None
        and evento.cuatrimestre_max is not None
        and usuario.cuatrimestre_actual is not None
        and evento.cuatrimestre_min <= usuario.cuatrimestre_actual <= evento.cuatrimestre_max
    ):
        score += 1
    return score


# ---------------------------------------------------------------------------
# Vistas públicas
# ---------------------------------------------------------------------------

def home(request):
    qs = (
        Evento.objects.select_related("escuela", "escuela__facultad")
        .annotate(inscritos_count=Count("inscripcion"))
        .order_by("fecha_evento")
    )

    # Filtros desde GET
    tipo = request.GET.get("tipo", "")
    escuela_id = request.GET.get("escuela", "")
    facultad_id = request.GET.get("facultad", "")
    lugar = request.GET.get("lugar", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")
    solo_cocurricular = request.GET.get("cocurricular", "")
    solo_virtual = request.GET.get("virtual", "")

    if tipo:
        qs = qs.filter(tipo=tipo)
    if escuela_id:
        qs = qs.filter(escuela_id=escuela_id)
    if facultad_id:
        qs = qs.filter(escuela__facultad_id=facultad_id)
    if lugar:
        qs = qs.filter(lugar__icontains=lugar)
    if fecha_desde:
        qs = qs.filter(fecha_evento__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_evento__lte=fecha_hasta)
    if solo_cocurricular == "1":
        qs = qs.filter(es_cocurricular=True)
    if solo_virtual == "1":
        qs = qs.exclude(enlace_virtual="")

    eventos = list(qs)

    # Personalización para estudiantes autenticados con escuela asignada
    eventos_prioritarios = []
    eventos_otros = []

    if (
        request.user.is_authenticated
        and request.user.rol == "ESTUDIANTE"
        and request.user.escuela_id
    ):
        for ev in eventos:
            if _calcular_prioridad(ev, request.user) >= 1:
                eventos_prioritarios.append(ev)
            else:
                eventos_otros.append(ev)
    else:
        eventos_otros = eventos

    context = {
        "eventos_prioritarios": eventos_prioritarios,
        "eventos_otros": eventos_otros,
        "facultades": Facultad.objects.all(),
        "escuelas": Escuela.objects.select_related("facultad").all(),
        "tipo_choices": Evento.TIPO_CHOICES,
        "filtros": {
            "tipo": tipo,
            "escuela": escuela_id,
            "facultad": facultad_id,
            "lugar": lugar,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "cocurricular": solo_cocurricular,
            "virtual": solo_virtual,
        },
    }
    return render(request, "sistema/home.html", context)


def detalle_evento(request, pk):
    evento = get_object_or_404(
        Evento.objects.select_related("escuela", "escuela__facultad", "publicado_por"),
        pk=pk,
    )
    inscritos = evento.inscripcion_set.count()
    cupos_disponibles = None
    if evento.cupo_maximo > 0:
        cupos_disponibles = max(0, evento.cupo_maximo - inscritos)

    ya_inscrito = False
    if request.user.is_authenticated:
        ya_inscrito = Inscripcion.objects.filter(
            usuario=request.user, evento=evento
        ).exists()

    puede_inscribirse = (
        request.user.is_authenticated
        and request.user.rol == "ESTUDIANTE"
        and not ya_inscrito
        and (
            evento.cupo_maximo == 0
            or (cupos_disponibles is not None and cupos_disponibles > 0)
        )
    )

    context = {
        "evento": evento,
        "cupos_disponibles": cupos_disponibles,
        "inscritos": inscritos,
        "ya_inscrito": ya_inscrito,
        "puede_inscribirse": puede_inscribirse,
    }
    return render(request, "sistema/evento_detalle.html", context)


def tesis_lista(request):
    qs = (
        Evento.objects.filter(tipo="TESIS")
        .select_related("escuela", "escuela__facultad")
        .annotate(inscritos_count=Count("inscripcion"))
        .order_by("fecha_evento")
    )
    q = request.GET.get("q", "")
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))

    context = {"tesis": qs, "query": q}
    return render(request, "sistema/tesis_lista.html", context)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class CustomLoginView(LoginView):
    template_name = "sistema/login.html"
    redirect_authenticated_user = True


def registro(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"¡Bienvenido, {user.first_name or user.username}!"
            )
            return redirect("home")
    else:
        form = RegistroForm()

    return render(request, "sistema/registro.html", {"form": form})


# ---------------------------------------------------------------------------
# Vistas de estudiante
# ---------------------------------------------------------------------------

@login_required
def inscribir_evento(request, pk):
    if request.method != "POST":
        return redirect("detalle_evento", pk=pk)

    if request.user.rol == "ADMIN":
        messages.error(request, "Los administradores no pueden inscribirse en eventos.")
        return redirect("detalle_evento", pk=pk)

    evento = get_object_or_404(Evento, pk=pk)

    with transaction.atomic():
        inscritos = (
            Inscripcion.objects.select_for_update()
            .filter(evento=evento)
            .count()
        )
        if evento.cupo_maximo > 0 and inscritos >= evento.cupo_maximo:
            messages.error(
                request, "Lo sentimos, no hay cupos disponibles para este evento."
            )
            return redirect("detalle_evento", pk=pk)

        inscripcion, created = Inscripcion.objects.get_or_create(
            usuario=request.user, evento=evento
        )

    if created:
        messages.success(
            request, f"¡Inscripción confirmada para «{evento.titulo}»!"
        )
    else:
        messages.info(request, "Ya estás inscrito en este evento.")

    return redirect("detalle_evento", pk=pk)


@login_required
def cancelar_inscripcion(request, pk):
    if request.method != "POST":
        return redirect("detalle_evento", pk=pk)

    inscripcion = get_object_or_404(
        Inscripcion, evento__pk=pk, usuario=request.user
    )

    if inscripcion.evento.fecha_evento <= timezone.now():
        messages.error(
            request,
            "No puedes cancelar la inscripción de un evento que ya ocurrió.",
        )
        return redirect("detalle_evento", pk=pk)

    inscripcion.delete()
    messages.success(request, "Inscripción cancelada exitosamente.")
    return redirect("detalle_evento", pk=pk)


@login_required
def perfil(request):
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")
    else:
        form = PerfilForm(instance=request.user)

    inscripciones = (
        Inscripcion.objects.filter(usuario=request.user)
        .select_related("evento", "evento__escuela")
        .order_by("evento__fecha_evento")
    )

    context = {"form": form, "inscripciones": inscripciones}
    return render(request, "sistema/perfil.html", context)


@login_required
def configuracion_notificaciones(request):
    config, _ = ConfiguracionNotificacion.objects.get_or_create(
        usuario=request.user
    )

    if request.method == "POST":
        form = ConfiguracionNotificacionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferencias de notificación guardadas.")
            return redirect("configuracion_notificaciones")
    else:
        form = ConfiguracionNotificacionForm(instance=config)

    return render(
        request,
        "sistema/configuracion_notificaciones.html",
        {"form": form},
    )


# ---------------------------------------------------------------------------
# Panel de administración
# ---------------------------------------------------------------------------

@admin_required
def admin_panel(request):
    total_eventos = Evento.objects.count()
    total_inscripciones = Inscripcion.objects.count()
    ahora = timezone.now()
    proximos = Evento.objects.filter(
        fecha_evento__gte=ahora,
        fecha_evento__lte=ahora + timezone.timedelta(days=30),
    ).count()

    eventos_recientes = (
        Evento.objects.select_related("escuela", "publicado_por")
        .annotate(inscritos_count=Count("inscripcion"))
        .order_by("-fecha_creacion")[:20]
    )

    context = {
        "total_eventos": total_eventos,
        "total_inscripciones": total_inscripciones,
        "proximos": proximos,
        "eventos_recientes": eventos_recientes,
    }
    return render(request, "sistema/admin_panel/panel.html", context)


@admin_required
def admin_evento_crear(request):
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.publicado_por = request.user
            evento.save()
            messages.success(
                request, f"Evento «{evento.titulo}» publicado exitosamente."
            )
            return redirect("admin_panel")
    else:
        form = EventoForm()

    return render(
        request,
        "sistema/admin_panel/evento_form.html",
        {"form": form, "accion": "Publicar evento"},
    )


@admin_required
def admin_evento_editar(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, f"Evento «{evento.titulo}» actualizado.")
            return redirect("admin_panel")
    else:
        form = EventoForm(instance=evento)

    return render(
        request,
        "sistema/admin_panel/evento_form.html",
        {"form": form, "evento": evento, "accion": "Guardar cambios"},
    )


@admin_required
def admin_evento_eliminar(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == "POST":
        titulo = evento.titulo
        evento.delete()
        messages.success(request, f"Evento «{titulo}» eliminado.")
        return redirect("admin_panel")

    return render(
        request,
        "sistema/admin_panel/evento_eliminar.html",
        {"evento": evento},
    )
