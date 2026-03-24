from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Evento, Inscripcion


def home(request):
    eventos = Evento.objects.all().order_by("-fecha_evento")
    return render(request, "home.html", {"eventos": eventos})


def detalle_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    cupos_ocupados = Inscripcion.objects.filter(evento=evento).count()
    cupos_disponibles = evento.cupo_maximo - cupos_ocupados

    return render(
        request,
        "detalle.html",
        {"evento": evento, "cupos_disponibles": cupos_disponibles},
    )


@login_required
def inscribir_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    cupos_ocupados = Inscripcion.objects.filter(evento=evento).count()

    if cupos_ocupados < evento.cupo_maximo:
        Inscripcion.objects.get_or_create(usuario=request.user, evento=evento)
        return redirect("home")
    else:
        return render(
            request,
            "detalle.html",
            {"evento": evento, "error": "Lo sentimos, no hay cupos."},
        )
