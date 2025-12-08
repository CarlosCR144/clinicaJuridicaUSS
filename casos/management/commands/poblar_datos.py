from django.core.management.base import BaseCommand
from casos.models import Tribunal, Materia

class Command(BaseCommand):
    help = 'Carga datos iniciales (Tribunales y Materias) para la Clínica Jurídica'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando carga de datos maestros...'))

        # --- 1. MATERIAS ---
        materias_data = [
            {'nombre': 'Civil', 'descripcion': 'Conflictos entre particulares, contratos, herencias, arrendamientos.'},
            {'nombre': 'Familia', 'descripcion': 'Divorcios, pensiones de alimentos, cuidado personal (tuición), VIF.'},
            {'nombre': 'Laboral', 'descripcion': 'Despidos injustificados, tutela de derechos fundamentales, cobro de prestaciones.'},
            {'nombre': 'Penal', 'descripcion': 'Delitos y faltas (representación de víctimas o imputados).'},
            {'nombre': 'Policía Local', 'descripcion': 'Infracciones de tránsito, ley del consumidor, conflictos vecinales.'},
        ]

        for data in materias_data:
            materia, created = Materia.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'descripcion': data['descripcion']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f' - Materia creada: {materia.nombre}'))
            else:
                self.stdout.write(f' - Materia ya existía: {materia.nombre}')

        # --- 2. TRIBUNALES (Ejemplo Región Metropolitana/General) ---
        # Puedes agregar tribunales específicos de Valdivia si es necesario por la sede de la USS
        tribunales_data = [
            {'nombre': 'Juzgado de Garantía', 'comuna': 'General'},
            {'nombre': 'Tribunal de Juicio Oral en lo Penal', 'comuna': 'General'},
            {'nombre': 'Juzgado de Familia', 'comuna': 'General'},
            {'nombre': 'Juzgado de Letras del Trabajo', 'comuna': 'General'},
            {'nombre': '1º Juzgado Civil', 'comuna': 'Valdivia'},
            {'nombre': '2º Juzgado Civil', 'comuna': 'Valdivia'},
            {'nombre': 'Juzgado de Policía Local', 'comuna': 'Valdivia'},
            {'nombre': 'Corte de Apelaciones', 'comuna': 'Valdivia'},
        ]

        for data in tribunales_data:
            tribunal, created = Tribunal.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'comuna': data['comuna']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f' - Tribunal creado: {tribunal.nombre}'))
            else:
                self.stdout.write(f' - Tribunal ya existía: {tribunal.nombre}')

        self.stdout.write(self.style.SUCCESS('¡Carga de datos finalizada correctamente!'))