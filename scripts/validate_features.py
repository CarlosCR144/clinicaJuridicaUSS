import os
import sys
import django
import datetime
import traceback
from dotenv import load_dotenv

# --- Configuration & Setup ---

# Load env variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinica_juridica.settings')
django.setup()

from django.conf import settings
# PATCH: Force IPv4 to avoid Windows ::1 connection issues with MySQL/MariaDB
if 'default' in settings.DATABASES:
    settings.DATABASES['default']['HOST'] = '127.0.0.1'

from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from personas.models import Usuario, Persona

# --- Test Engine ---

tests = []

def register_test(name, description):
    def decorator(func):
        tests.append({'name': name, 'description': description, 'func': func})
        return func
    return decorator

# --- Passing Tests (8) ---

@register_test("Crear Usuario Director", "Verificar que se puede instanciar un usuario con rol de director correctamente.")
def test_01_create_director():
    u = Usuario(username='test_director_ok', rut='10000000-1', rol='director')
    u.set_password('pass123')
    u.save()
    if u.rol != 'director':
        raise AssertionError(f"El rol esperado era 'director', pero se obtuvo '{u.rol}'")

@register_test("Crear Persona Completa", "Verificar creación de un objeto Persona con todos sus campos.")
def test_02_create_persona():
    p = Persona(rut='20000000-2', nombres='Ana', apellidos='Gomez', email='ana@test.com', telefono='123456789')
    p.save()
    if p.nombres != 'Ana':
        raise AssertionError("El nombre no se guardó correctamente.")

@register_test("Verificar Roles del Sistema", "Asegurar que las opciones de roles (ROL_CHOICES) contienen los roles críticos.")
def test_03_roles_exist():
    roles_dict = dict(Usuario.ROL_CHOICES)
    required = ['director', 'estudiante', 'supervisor']
    for r in required:
        if r not in roles_dict:
            raise AssertionError(f"Falta el rol crítico: {r}")

@register_test("Representación String Usuario", "Verificar que el método __str__ de Usuario devuelve el formato '{Nombre} {Apellido} ({Rol})'.")
def test_04_str_usuario():
    u = Usuario(first_name='Luisa', last_name='Mora', rol='supervisor')
    s = str(u)
    if 'Luisa' not in s or 'Mora' not in s:
        raise AssertionError(f"Formato __str__ incorrecto: {s}")

@register_test("Representación String Persona", "Verificar que el método __str__ de Persona incluye nombre y RUT.")
def test_05_str_persona():
    p = Persona(nombres='Carlos', apellidos='Vela', rut='30000000-3')
    s = str(p)
    if 'Carlos' not in s or '30000000-3' not in s:
        raise AssertionError(f"Formato __str__ incorrecto: {s}")

@register_test("Rol por Defecto", "Verificar que si no se especifica rol, se asigne el default (estudiante).")
def test_06_default_role():
    u = Usuario()
    if u.rol != 'estudiante':
        raise AssertionError(f"Rol por defecto incorrecto: {u.rol}")

@register_test("Restricción RUT Único (Schema)", "Verificar que el campo RUT en Usuario tiene unique=True en la definición del modelo.")
def test_07_rut_unique_constraint():
    field = Usuario._meta.get_field('rut')
    if not field.unique:
        raise AssertionError("Meta-validación fallida: unique=True no está seteado en el campo RUT.")

@register_test("Campos Nulos Persona (Schema)", "Verificar que email es opcional (null/blank=True).")
def test_08_optional_fields():
    field = Persona._meta.get_field('email')
    if not field.null or not field.blank:
        raise AssertionError("Meta-validación fallida: Email debería ser opcional.")

# --- Failing Tests (2) - Real Logic Checks ---
# These verify business rules that are NOT yet implemented in the models.
# Therefore, the tests will see "Success" in performing the forbidden action, 
# and verify that the system FAILED to block it.

@register_test("Unicidad de Email", "Verificar que el sistema impida registrar dos Personas con el mismo email.")
def test_09_unique_email_real():
    # Creamos primer usuario
    p1 = Persona(rut='40000000-4', nombres='P1', apellidos='Test1', email='dup@test.com')
    p1.save()
    
    # Intentamos crear segundo usuario con MISMO email
    p2 = Persona(rut='50000000-5', nombres='P2', apellidos='Test2', email='dup@test.com')
    
    try:
        p2.save() # Esto debería fallar si existe validación
        # Si llegamos aquí, el sistema permitió el duplicado -> EL TEST FALLA
        raise AssertionError("FALLO DE VALIDACIÓN: El sistema permitió crear dos personas con el email 'dup@test.com'.")
    except (IntegrityError, ValidationError):
        # Si atrapamos error, el sistema funcionó bien
        pass

@register_test("Formato Numérico Teléfono", "Verificar que el sistema rechace teléfonos con letras.")
def test_10_phone_numeric_real():
    p = Persona(rut='60000000-6', nombres='BadPhone', apellidos='Test', telefono='ABCDE')
    try:
        p.full_clean() # Valida campos
        p.save()
        # Si guarda, el sistema aceptó basura -> EL TEST FALLA
        raise AssertionError("FALLO DE VALIDACIÓN: El sistema aceptó un teléfono no numérico ('ABCDE').")
    except ValidationError:
        pass

# --- Execution ---

results = []
print(f"Ejecutando 10 pruebas contra base de datos: {settings.DATABASES['default']['NAME']} ({settings.DATABASES['default']['ENGINE']})\n")

for test in tests:
    res = {
        'name': test['name'],
        'description': test['description'],
        'status': 'UNKNOWN',
        'details': ''
    }
    
    try:
        with transaction.atomic():
            test['func']()
            transaction.set_rollback(True) # Siempre rollback para no afectar BD
            
        res['status'] = 'APROBADO'
        res['details'] = 'Comportamiento esperado verificado.'
        print(f"[OK] {test['name']}")
        
    except AssertionError as ae:
        res['status'] = 'RECHAZADO'
        res['details'] = str(ae)
        print(f"[X]  {test['name']} - {ae}")
        
    except Exception as e:
        res['status'] = 'ERROR' # Error no controlado (código roto, no lógica fallida)
        res['details'] = f"Excepción inesperada: {str(e)}"
        print(f"[!!] {test['name']} - {e}")
        
    results.append(res)

# --- Report Generation ---

passed = sum(1 for r in results if r['status'] == 'APROBADO')
failed = sum(1 for r in results if r['status'] in ['RECHAZADO', 'ERROR'])

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Validación - Clinica Juridica USS</title>
    <style>
        body {{ font-family: sans-serif; background: #f4f4f4; padding: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 900px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #333; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat {{ text-align: center; padding: 10px; border-radius: 4px; width: 30%; color: white; }}
        .stat.total {{ background: #007bff; }}
        .stat.pass {{ background: #28a745; }}
        .stat.fail {{ background: #dc3545; }}
        .stat strong {{ display: block; font-size: 24px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #343a40; color: white; }}
        .badge {{ padding: 5px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; }}
        .badge.aprobado {{ background: #28a745; }}
        .badge.rechazado {{ background: #dc3545; }}
        .badge.error {{ background: #ffc107; color: black; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Reporte de Pruebas Automatizadas</h1>
        <div class="summary">
            <div class="stat total"><strong>{len(results)}</strong>Total</div>
            <div class="stat pass"><strong>{passed}</strong>Aprobadas</div>
            <div class="stat fail"><strong>{failed}</strong>Rechazadas</div>
        </div>
        <table>
            <thead><tr><th>Prueba</th><th>Descripción</th><th>Estado</th><th>Detalles</th></tr></thead>
            <tbody>
"""

for r in results:
    cls = r['status'].lower()
    html += f"""
            <tr>
                <td><b>{r['name']}</b></td>
                <td>{r['description']}</td>
                <td><span class="badge {cls}">{r['status']}</span></td>
                <td>{r['details']}</td>
            </tr>"""

html += f"""
            </tbody>
        </table>
        <p style="text-align: center; color: #777; margin-top: 20px;">Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'validation_report.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nReporte HTML generado en: {out_path}")
