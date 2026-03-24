from django.contrib import admin
from .models import Facultad, Escuela, Evento, Inscripcion, Usuario

admin.site.register(Facultad)
admin.site.register(Escuela)
admin.site.register(Evento)
admin.site.register(Inscripcion)
admin.site.register(Usuario)
