# Sistema de Notificaciones por Correo

Guía técnica del sistema de correos automáticos de la plataforma **UNPHU Eventos**.

---

## Resumen

El sistema envía correos electrónicos en tres situaciones:

| Evento que lo dispara | Correo enviado | Destino |
|---|---|---|
| Estudiante se inscribe a un evento | Confirmación de inscripción | El estudiante inscrito |
| Se publica un nuevo evento | Anuncio de nueva actividad | Estudiantes de la misma escuela o facultad |
| Cron diario/horario | Recordatorio de evento próximo | Estudiantes con evento en N días |

Cada usuario puede activar o desactivar individualmente cada tipo de notificación desde **Mi perfil → Notificaciones** (`/perfil/notificaciones/`).

---

## 1. Confirmación de inscripción

**Cuándo:** Inmediatamente después de que un estudiante se inscribe a un evento.

**Mecanismo:** Señal Django `post_save` sobre el modelo `Inscripcion` (solo en creación, `created=True`).

**Archivo:** `sistema/signals.py` → función `enviar_confirmacion_inscripcion`

**Respeta la preferencia:** `ConfiguracionNotificacion.confirmacion_inscripcion`

**Plantilla de correo:** `sistema/templates/sistema/emails/confirmacion_inscripcion.txt`

**Contenido del correo:**
```
Hola {nombre},

Tu inscripción al siguiente evento ha sido confirmada exitosamente:

  Evento:  {titulo}
  Tipo:    {tipo}
  Fecha:   {fecha y hora}
  Lugar:   {lugar}
  Escuela: {escuela}
```

**Flujo:**
1. El estudiante hace clic en "Inscribirse" en la vista de detalle del evento.
2. La vista `inscribir_evento` crea un registro `Inscripcion` dentro de `transaction.atomic()`.
3. Django dispara automáticamente la señal `post_save`.
4. La señal verifica que el usuario tenga `confirmacion_inscripcion=True` y que tenga correo.
5. Se llama a `send_mail(..., fail_silently=True)` — si el servidor SMTP falla, **no** se revierte la inscripción.

---

## 2. Anuncio de nuevo evento

**Cuándo:** Inmediatamente después de que un administrador publica un nuevo evento.

**Mecanismo:** Señal Django `post_save` sobre el modelo `Evento` (solo en creación, `created=True`).

**Archivo:** `sistema/signals.py` → función `notificar_nuevo_evento`

**Respeta las preferencias:**
- `ConfiguracionNotificacion.notificar_nueva_actividad_escuela` — para estudiantes de la misma escuela del evento
- `ConfiguracionNotificacion.notificar_nueva_actividad_facultad` — para estudiantes de otras escuelas de la misma facultad

**Plantilla de correo:** `sistema/templates/sistema/emails/nuevo_evento_escuela.txt`

**Lógica de destinatarios:**
```
destinatarios = (
    estudiantes de la misma escuela con notificar_nueva_actividad_escuela=True
    ∪
    estudiantes de otras escuelas de la misma facultad con notificar_nueva_actividad_facultad=True
)
```

Si el evento no tiene escuela asignada, o la escuela no tiene facultad, la segunda lista quedará vacía — no hay error.

**Flujo:**
1. El administrador guarda un nuevo evento desde `/gestion/evento/nuevo/` o desde el Django Admin.
2. Django dispara la señal `post_save`.
3. La señal construye el conjunto de correos destinatarios (usando `values_list("email", flat=True)`).
4. Si hay al menos un destinatario, envía un único `send_mail` con todos los correos (`fail_silently=True`).

> **Nota:** El correo se envía como lista de destinatarios visibles entre sí (`To` múltiple). Para producción considerar envío individual o uso de `bcc`.

---

## 3. Recordatorio de evento próximo

**Cuándo:** Se ejecuta manualmente o via cron, normalmente cada hora.

**Mecanismo:** Comando de administración Django.

**Archivo:** `sistema/management/commands/enviar_recordatorios.py`

**Respeta las preferencias:**
- `ConfiguracionNotificacion.recordatorio_evento` — si el usuario desactivó recordatorios, se omite
- `ConfiguracionNotificacion.dias_recordatorio` — cuántos días antes enviar el recordatorio (por defecto: 1 día)

**Plantilla de correo:** `sistema/templates/sistema/emails/recordatorio_evento.txt`

**Algoritmo de ventana de tiempo:**

```python
ahora = timezone.now()
ventana_inicio = ahora + timedelta(days=dias) - timedelta(hours=1)
ventana_fin    = ahora + timedelta(days=dias) + timedelta(hours=1)

# Solo enviar si el evento cae dentro de ±1 hora alrededor del target
if ventana_inicio <= evento.fecha_evento <= ventana_fin:
    enviar_recordatorio()
```

Esto garantiza que aunque el cron se ejecute cada hora, el recordatorio se envíe una sola vez cerca del momento exacto configurado por el usuario.

**Cómo ejecutar manualmente:**
```bash
source .venv/bin/activate
python manage.py enviar_recordatorios
```

**Configuración de cron (ejecutar cada hora):**
```bash
0 * * * * /ruta/al/venv/bin/python /ruta/al/proyecto/manage.py enviar_recordatorios >> /var/log/unphu_recordatorios.log 2>&1
```

**Flujo:**
1. El comando carga todas las inscripciones con `recordatorio_enviado=False`, evento futuro, y `recordatorio_evento=True`.
2. Por cada inscripción, calcula la ventana objetivo según `dias_recordatorio` del usuario.
3. Si el evento cae en la ventana, envía el correo (`fail_silently=False` en este caso para registrar errores en log).
4. Marca `inscripcion.recordatorio_enviado = True` (con `update_fields` para eficiencia).
5. Imprime un resumen en stdout: `N recordatorio(s) enviado(s), N error(es)`.

---

## Configuración por usuario (`ConfiguracionNotificacion`)

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `confirmacion_inscripcion` | Boolean | `True` | Recibir correo al inscribirse |
| `recordatorio_evento` | Boolean | `True` | Recibir recordatorio antes del evento |
| `dias_recordatorio` | Entero positivo | `1` | Cuántos días antes enviar el recordatorio |
| `notificar_nueva_actividad_escuela` | Boolean | `True` | Recibir aviso de nuevos eventos de mi escuela |
| `notificar_nueva_actividad_facultad` | Boolean | `False` | Recibir aviso de nuevos eventos de mi facultad |

**Creación automática:** Al registrarse un nuevo usuario, la señal `post_save` sobre `Usuario` crea automáticamente su `ConfiguracionNotificacion` con los valores por defecto. El usuario nunca necesita crearla manualmente.

---

## Backend de correo

### Desarrollo (actual)
```python
# unphu_eventos/settings.py
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```
Los correos se imprimen en la consola del servidor. No se envían realmente. Útil para ver el contenido exacto durante desarrollo.

### Producción
Reemplazar con SMTP real, por ejemplo con Gmail o SendGrid:
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "tu-cuenta@gmail.com"
EMAIL_HOST_PASSWORD = "tu-app-password"
DEFAULT_FROM_EMAIL = "UNPHU Eventos <no-reply@unphu.edu.do>"
```

---

## Estructura de archivos relevantes

```
sistema/
├── signals.py                          # Señales: confirmación + anuncio de nuevo evento
├── apps.py                             # Registra signals en ready()
├── models.py                           # ConfiguracionNotificacion
├── management/
│   └── commands/
│       └── enviar_recordatorios.py     # Comando de recordatorios (cron)
└── templates/sistema/emails/
    ├── confirmacion_inscripcion.txt    # Plantilla: confirmación de inscripción
    ├── nuevo_evento_escuela.txt        # Plantilla: anuncio de nuevo evento
    └── recordatorio_evento.txt        # Plantilla: recordatorio de evento próximo
```

---

## Consideraciones para producción

1. **Envío masivo:** El anuncio de nuevo evento usa `To` múltiple. Si hay muchos estudiantes, considerar envío individual o servicio como SendGrid/Mailgun con soporte para bulk email.
2. **Rate limiting:** Gmail tiene límite de ~500 correos/día en cuentas normales. Para mayor volumen usar un proveedor transaccional.
3. **Zona horaria:** El comando `enviar_recordatorios` usa `timezone.now()` que respeta `TIME_ZONE = "America/Santo_Domingo"` configurado en settings.
4. **Idempotencia:** El campo `recordatorio_enviado=True` evita duplicados aunque el cron se ejecute varias veces en la misma hora.
5. **Logs:** Redirigir stdout del cron a un archivo de log para auditar envíos y errores.
