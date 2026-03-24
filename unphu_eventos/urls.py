from django.contrib import admin
from django.urls import path
from sistema import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("evento/<int:evento_id>/", views.detalle_evento, name="detalle_evento"),
    path(
        "evento/<int:evento_id>/inscribir/",
        views.inscribir_evento,
        name="inscribir_evento",
    ),
]
