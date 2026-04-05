"""
Carga eventos de demostración variados para probar todas las funcionalidades
del sistema. Se ejecuta con: python manage.py cargar_eventos_demo

Es seguro correrlo múltiples veces — usa get_or_create por título+fecha.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sistema.models import Escuela, Evento


EVENTOS = [
    # ── PRESENTACIONES DE TESIS ─────────────────────────────────────────────
    {
        "titulo": "Defensa de Tesis: Sistema de Gestión de Inventarios con IA",
        "descripcion": (
            "El estudiante Fraiman Lara presentará su proyecto de grado sobre un sistema de "
            "gestión de inventarios que integra modelos de inteligencia artificial para predicción "
            "de demanda y optimización de stock en pequeñas y medianas empresas dominicanas."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 60,
        "fecha_evento": "2026-04-15T09:00:00",
        "fecha_fin":    "2026-04-15T11:00:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Auditorio Principal — Edificio A",
        "defensor":     "Fraiman Lara",
        "jurados":      "Dr. Carlos Méndez\nIng. Rosa Belén Castillo\nIng. José Rodríguez",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Defensa de Tesis: Plataforma Web de Telemedicina para Zonas Rurales",
        "descripcion": (
            "La estudiante María González presenta su investigación sobre el diseño e "
            "implementación de una plataforma web de telemedicina orientada a facilitar el acceso "
            "a servicios de salud en comunidades rurales de la República Dominicana."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 50,
        "fecha_evento": "2026-04-18T10:00:00",
        "fecha_fin":    "2026-04-18T12:00:00",
        "escuela":      "Escuela de Medicina",
        "lugar":        "Salón de Conferencias — Edificio de Salud, Piso 3",
        "defensor":     "María González",
        "jurados":      "Dra. Elena Soriano\nDr. Fernando Vargas\nDra. Miriam Castillo",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Defensa de Tesis: Análisis Estructural de Puentes Peatonales Urbanos",
        "descripcion": (
            "El estudiante Esteban Zabala expondrá su proyecto de grado sobre el análisis "
            "estructural y propuesta de diseño para puentes peatonales en zonas urbanas del "
            "Gran Santo Domingo, aplicando normas AASHTO y criterios locales MOPC."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 45,
        "fecha_evento": "2026-04-22T14:00:00",
        "fecha_fin":    "2026-04-22T16:30:00",
        "escuela":      "Escuela de Ingeniería Civil",
        "lugar":        "Aula Magna — Facultad de Ciencias y Tecnología",
        "defensor":     "Esteban Zabala",
        "jurados":      "Ing. Ramón Torres\nIng. Patricia Almánzar\nDr. Luis Féliz",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Defensa de Tesis: Estrategias de Marketing Digital para PYMEs en RD",
        "descripcion": (
            "La estudiante Carolina Méndez presenta su tesis sobre estrategias de marketing "
            "digital adaptadas al contexto dominicano para pequeñas y medianas empresas, con "
            "énfasis en redes sociales, SEO y analítica web."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 40,
        "fecha_evento": "2026-04-25T09:30:00",
        "fecha_fin":    "2026-04-25T11:30:00",
        "escuela":      "Escuela de Administración de Empresas",
        "lugar":        "Sala de Conferencias — Edificio de Empresariales, Piso 2",
        "defensor":     "Carolina Méndez",
        "jurados":      "Dr. Manuel Henríquez\nLic. Sandra Pérez\nLic. Roberto Almonte",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Defensa de Tesis: Diseño Bioclimático en Viviendas de Interés Social",
        "descripcion": (
            "La estudiante Valeria Rodríguez presentará su proyecto sobre aplicación de "
            "principios bioclimáticos al diseño de viviendas de interés social en el clima "
            "tropical dominicano, buscando reducir el consumo energético."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 35,
        "fecha_evento": "2026-05-02T10:00:00",
        "fecha_fin":    "2026-05-02T12:00:00",
        "escuela":      "Escuela de Arquitectura y Urbanismo",
        "lugar":        "Sala de Exposiciones — Escuela de Arquitectura",
        "defensor":     "Valeria Rodríguez",
        "jurados":      "Arq. Laura Soto\nArq. David Núñez\nDr. Carlos Fernández",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Defensa de Tesis: Aplicación Móvil para la Gestión de Citas Médicas",
        "descripcion": (
            "El estudiante Marvin Hernández presentará su proyecto de grado sobre el desarrollo "
            "de una aplicación móvil multiplataforma (Flutter) para la gestión de citas médicas "
            "en clínicas privadas de Santo Domingo, integrando recordatorios automáticos y "
            "historial clínico básico."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 55,
        "fecha_evento": "2026-05-06T09:00:00",
        "fecha_fin":    "2026-05-06T11:00:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Auditorio Principal — Edificio A",
        "defensor":     "Marvin Hernández",
        "jurados":      "Ing. Sergio Cabral\nIng. Paola Jiménez\nDr. Alberto Rosario",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Defensa de Tesis: Impacto del Código Procesal Penal en los Derechos del Imputado",
        "descripcion": (
            "La estudiante Stephanie Núñez presentará su tesis sobre el análisis comparativo "
            "del impacto del Código Procesal Penal dominicano en la protección de los derechos "
            "fundamentales del imputado, con énfasis en presunción de inocencia y defensa técnica."
        ),
        "tipo": "TESIS",
        "cupo_maximo": 35,
        "fecha_evento": "2026-05-14T10:00:00",
        "fecha_fin":    "2026-05-14T12:30:00",
        "escuela":      "Escuela de Derecho",
        "lugar":        "Salón de Actos — Facultad de Ciencias Jurídicas, Piso 2",
        "defensor":     "Stephanie Núñez",
        "jurados":      "Dr. Francisco Peña\nDra. Carmen Luisa Tejeda\nDr. Rafael Almánzar",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },

    # ── ACTIVIDADES ACADÉMICAS ───────────────────────────────────────────────
    {
        "titulo": "Charla: Introducción a la Ciberseguridad y Ethical Hacking",
        "descripcion": (
            "Conferencia a cargo del Ing. Marcos Jiménez (certificado CEH) sobre conceptos "
            "fundamentales de ciberseguridad ofensiva y defensiva. Se abordarán vectores de "
            "ataque comunes, metodologías de pentesting y cómo las organizaciones dominicanas "
            "pueden proteger sus activos digitales.\n\n"
            "Dirigido a estudiantes de Informática e Ingeniería. No se requieren conocimientos "
            "previos avanzados."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 80,
        "fecha_evento": "2026-04-10T16:00:00",
        "fecha_fin":    "2026-04-10T18:00:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Laboratorio de Cómputo 3 — Edificio B, Piso 1",
        "cuatrimestre_min": 3, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Taller: Desarrollo de APIs REST con Django y Django REST Framework",
        "descripcion": (
            "Taller práctico de 3 horas sobre el desarrollo de APIs RESTful usando Python y "
            "Django REST Framework. Los participantes construirán una API funcional desde cero, "
            "aplicando JWT, serializers, viewsets y documentación automática con Swagger.\n\n"
            "Requisito: traer laptop con Python 3.11+ instalado. Cupos muy limitados."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 25,
        "fecha_evento": "2026-04-12T09:00:00",
        "fecha_fin":    "2026-04-12T12:00:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Laboratorio de Desarrollo de Software — Edificio B, Piso 2",
        "cuatrimestre_min": 5, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Seminario: Inteligencia Artificial Generativa y su Impacto en el Mercado Laboral",
        "descripcion": (
            "Panel de expertos sobre el impacto de la IA generativa (ChatGPT, Copilot, Gemini) "
            "en el mercado laboral tecnológico dominicano y regional. Se discutirán oportunidades "
            "de especialización, nuevos perfiles y las competencias que los graduados deben "
            "desarrollar para mantenerse competitivos.\n\n"
            "Panelistas: CEO de TechRD, Director de Innovación del Banco Popular, "
            "Directora académica de ITLA."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 100,
        "fecha_evento": "2026-04-17T15:00:00",
        "fecha_fin":    "2026-04-17T17:30:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Auditorio Principal — Edificio A",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Taller: Diseño de Estructuras de Concreto con ETABS",
        "descripcion": (
            "Taller práctico sobre el uso del software ETABS para análisis y diseño estructural "
            "de edificaciones de concreto reforzado. Se modelará un edificio de 5 niveles "
            "aplicando el Reglamento MOPC R-001 y la norma ACI 318.\n\n"
            "Requisito: conocimientos básicos de análisis estructural. Traer laptop con "
            "ETABS instalado (licencia de prueba disponible en el sitio oficial)."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 30,
        "fecha_evento": "2026-04-19T08:00:00",
        "fecha_fin":    "2026-04-19T12:00:00",
        "escuela":      "Escuela de Ingeniería Civil",
        "lugar":        "Sala de CAD — Ingeniería Civil, Piso 3",
        "cuatrimestre_min": 6, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Charla: Emprendimiento Legal — Cómo Constituir tu Empresa en RD",
        "descripcion": (
            "El Dr. Héctor Martínez, abogado corporativo con 15 años de experiencia, explicará "
            "el proceso legal para la constitución de empresas en República Dominicana, tipos "
            "societarios (SRL, SA), registro mercantil, aspectos tributarios DGII y protección "
            "de propiedad intelectual.\n\n"
            "Ideal para estudiantes próximos a graduarse con ideas de negocios."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 60,
        "fecha_evento": "2026-04-24T17:00:00",
        "fecha_fin":    "2026-04-24T19:00:00",
        "escuela":      "Escuela de Derecho",
        "lugar":        "Aula 301 — Edificio de Derecho, Piso 3",
        "cuatrimestre_min": 7, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Taller de Mindfulness y Manejo del Estrés Académico",
        "descripcion": (
            "Sesión práctica guiada por la Dra. Ana Belén Reyes, psicóloga clínica, orientada "
            "a estudiantes en etapas de alta exigencia académica (semestres finales, trabajo de "
            "grado). Se abordarán técnicas de respiración, meditación guiada y estrategias "
            "cognitivas para manejar la ansiedad ante exámenes y presentaciones."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 40,
        "fecha_evento": "2026-04-29T14:00:00",
        "fecha_fin":    "2026-04-29T16:00:00",
        "escuela":      "Escuela de Psicología",
        "lugar":        "Sala de Bienestar Estudiantil — Edificio Administrativo, Piso 1",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Charla: Contabilidad Forense y Detección de Fraudes Financieros",
        "descripcion": (
            "El CPA Miguel Ángel Ortiz compartirá su experiencia en auditoría forense y "
            "detección de irregularidades contables en empresas dominicanas. Se analizarán "
            "casos reales (anonimizados), técnicas de auditoría digital y el rol del contador "
            "en investigaciones judiciales."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 50,
        "fecha_evento": "2026-04-16T16:00:00",
        "fecha_fin":    "2026-04-16T18:00:00",
        "escuela":      "Escuela de Contabilidad y Auditoría",
        "lugar":        "Aula 202 — Edificio de Ciencias Económicas",
        "cuatrimestre_min": 5, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Taller de Fotografía Arquitectónica con Smartphone",
        "descripcion": (
            "Taller práctico para estudiantes de Arquitectura y Diseño sobre técnicas de "
            "fotografía arquitectónica usando únicamente el smartphone. Se abordarán "
            "composición, manejo de luz natural, edición con Lightroom Mobile y uso efectivo "
            "de imágenes en portafolios digitales."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 20,
        "fecha_evento": "2026-04-26T10:00:00",
        "fecha_fin":    "2026-04-26T13:00:00",
        "escuela":      "Escuela de Arquitectura y Urbanismo",
        "lugar":        "Patio de la Escuela de Arquitectura",
        "cuatrimestre_min": 3, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Hackathon UNPHU 2026: Soluciones Tech para la Salud",
        "descripcion": (
            "Primera edición del Hackathon UNPHU. Equipos de 3 a 5 personas tendrán 24 horas "
            "para desarrollar soluciones tecnológicas orientadas a mejorar el sistema de salud "
            "dominicano. Se evaluará impacto, viabilidad técnica y presentación.\n\n"
            "Premios:\n"
            "🥇 1er lugar: RD$ 50,000 + mentoría empresarial\n"
            "🥈 2do lugar: RD$ 25,000\n"
            "🥉 3er lugar: RD$ 10,000\n\n"
            "Inscripciones abiertas hasta el 25 de abril. Equipos multidisciplinarios son bienvenidos."
        ),
        "tipo": "ACADEMICA",
        "cupo_maximo": 120,
        "fecha_evento": "2026-05-09T08:00:00",
        "fecha_fin":    "2026-05-10T10:00:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Laboratorios de Informática — Edificio B, Pisos 1 y 2",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },

    # ── EVENTOS INSTITUCIONALES ──────────────────────────────────────────────
    {
        "titulo": "Ceremonia de Premiación: Mejores Promedios del Año Académico 2025",
        "descripcion": (
            "Ceremonia institucional en la que se reconocerá a los estudiantes con los promedios "
            "más altos de todas las facultades durante el año académico 2025. Asistirán "
            "autoridades universitarias, familiares de los homenajeados y representantes del "
            "cuerpo docente.\n\n"
            "Entrada libre para toda la comunidad universitaria. Vestimenta: formal."
        ),
        "tipo": "INSTITUCIONAL",
        "cupo_maximo": 0,
        "fecha_evento": "2026-05-07T18:00:00",
        "fecha_fin":    "2026-05-07T20:00:00",
        "escuela":      "Escuela de Informática",
        "lugar":        "Auditorio Principal — Edificio A",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Feria de Empleo UNPHU 2026 — Conecta con más de 40 Empresas",
        "descripcion": (
            "La Feria de Empleo UNPHU reúne a más de 40 empresas líderes de los sectores "
            "tecnológico, financiero, legal, construcción y salud. Los estudiantes podrán "
            "entregar su currículum, realizar entrevistas on-the-spot y conocer programas "
            "de pasantías y puestos de entrada.\n\n"
            "Empresas confirmadas: Claro RD, Banco BHD, Veektor, AES Dominicana, "
            "Grupo Ramos, entre otras.\n\n"
            "Trae múltiples copias de tu CV y vestimenta formal o semi-formal."
        ),
        "tipo": "INSTITUCIONAL",
        "cupo_maximo": 0,
        "fecha_evento": "2026-04-30T09:00:00",
        "fecha_fin":    "2026-04-30T15:00:00",
        "escuela":      "Escuela de Administración de Empresas",
        "lugar":        "Patio Central — Campus UNPHU",
        "cuatrimestre_min": 7, "cuatrimestre_max": 10,
    },
    {
        "titulo": "Aviso: Actualización del Calendario Académico — Semestre Mayo-Agosto 2026",
        "descripcion": (
            "La Dirección Académica informa que el calendario del semestre Mayo-Agosto 2026 "
            "ha sido actualizado con las siguientes modificaciones:\n\n"
            "• Inicio de clases: 5 de mayo de 2026\n"
            "• Primer parcial: semana del 9 al 13 de junio\n"
            "• Segundo parcial: semana del 14 al 18 de julio\n"
            "• Exámenes finales: del 10 al 22 de agosto\n"
            "• Cierre de notas: 28 de agosto\n\n"
            "Consultar el calendario completo en el portal institucional UNPHUSIST."
        ),
        "tipo": "INSTITUCIONAL",
        "cupo_maximo": 0,
        "fecha_evento": "2026-04-20T08:00:00",
        "fecha_fin":    None,
        "escuela":      "Escuela de Informática",
        "lugar":        "Virtual — Portal Institucional",
        "cuatrimestre_min": None, "cuatrimestre_max": None,
    },
    {
        "titulo": "Aviso: Convocatoria de Beca de Excelencia Académica 2026",
        "descripcion": (
            "La Oficina de Becas y Asuntos Estudiantiles informa que están abiertas las "
            "postulaciones para la Beca de Excelencia Académica 2026, dirigida a estudiantes "
            "con índice académico igual o superior a 90 y sin materias reprobadas.\n\n"
            "Beneficios: cubierta del 50% al 100% de la matrícula del semestre Mayo-Agosto 2026.\n\n"
            "Fecha límite de aplicación: 30 de abril de 2026.\n"
            "Documentos requeridos: récord de notas, carta de motivación, "
            "carta de recomendación docente.\n\n"
            "Información en la Oficina de Becas, Edificio Administrativo, Piso 2."
        ),
        "tipo": "INSTITUCIONAL",
        "cupo_maximo": 0,
        "fecha_evento": "2026-04-08T08:00:00",
        "fecha_fin":    None,
        "escuela":      "Escuela de Informática",
        "lugar":        "Oficina de Becas — Edificio Administrativo, Piso 2",
        "cuatrimestre_min": 3, "cuatrimestre_max": 10,
    },
]


class Command(BaseCommand):
    help = "Carga eventos de demostración para probar el sistema"

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0
        error_count = 0

        escuelas = {e.nombre: e for e in Escuela.objects.all()}

        for data in EVENTOS:
            escuela_nombre = data.pop("escuela")
            fecha_str = data.pop("fecha_evento")
            fecha_fin_str = data.pop("fecha_fin")

            escuela = escuelas.get(escuela_nombre)
            if not escuela:
                self.stderr.write(f"  ✗ Escuela no encontrada: '{escuela_nombre}' — omitiendo")
                error_count += 1
                data["escuela"] = escuela_nombre  # restaurar para siguiente iteración
                continue

            from django.utils.dateparse import parse_datetime
            from django.utils import timezone as tz

            fecha = parse_datetime(fecha_str)
            fecha_fin = parse_datetime(fecha_fin_str) if fecha_fin_str else None

            # Hacer aware si la BD usa timezone
            from django.conf import settings as dj_settings
            if dj_settings.USE_TZ:
                import zoneinfo
                tz_obj = zoneinfo.ZoneInfo(dj_settings.TIME_ZONE)
                if fecha and fecha.tzinfo is None:
                    fecha = fecha.replace(tzinfo=tz_obj)
                if fecha_fin and fecha_fin.tzinfo is None:
                    fecha_fin = fecha_fin.replace(tzinfo=tz_obj)

            evento, created = Evento.objects.update_or_create(
                titulo=data["titulo"],
                fecha_evento=fecha,
                defaults={
                    **data,
                    "escuela": escuela,
                    "fecha_fin": fecha_fin,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Creado: {evento.titulo[:60]}")
            else:
                skipped_count += 1
                self.stdout.write(f"  · Actualizado: {evento.titulo[:60]}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nResumen: {created_count} evento(s) creado(s), "
                f"{skipped_count} actualizado(s), {error_count} error(es)."
            )
        )
