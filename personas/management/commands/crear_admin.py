from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea un usuario administrador (Superuser) por defecto con rol Admin'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # Datos del Admin por defecto
        username = 'admin'
        password = '123'  # Contraseña
        email = 'admin@mail.cl'
        rut_admin = '12345678-9'
        
        # Verificamos si ya existe para no romper nada
        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Creando usuario "{username}"...')
            
            # create_superuser se encarga de is_staff=True e is_superuser=True
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                rut=rut_admin
            )
            
            admin_user.rol = 'admin'
            admin_user.first_name = 'Administrador'
            admin_user.last_name = 'Sistema'
            admin_user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ ÉXITO: Usuario creado.'))
            self.stdout.write(self.style.SUCCESS(f'   User: {username}'))
            self.stdout.write(self.style.SUCCESS(f'   Pass: {password}'))
            self.stdout.write(self.style.SUCCESS(f'   Rol:  {admin_user.rol}'))
        else:
            # Si ya existe, nos aseguramos de corregirle el rol por si acaso
            user = User.objects.get(username=username)
            if user.rol != 'admin':
                user.rol = 'admin'
                user.save()
                self.stdout.write(self.style.WARNING(f'⚠️ El usuario "{username}" ya existía. Se corrigió su rol a "admin".'))
            else:
                self.stdout.write(self.style.WARNING(f'El usuario "{username}" ya existe y está configurado correctamente.'))