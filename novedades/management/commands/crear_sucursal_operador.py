import secrets
import string
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from novedades.models import PerfilUsuario, Sucursal
from novedades.permisos import configurar_grupos_permisos


def generar_password_segura(longitud=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*"),
    ]
    password += [secrets.choice(caracteres) for _ in range(longitud - 4)]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


class Command(BaseCommand):
    help = (
        "Crea o actualiza una Sucursal y provisiona su usuario Operador asignado "
        "con aislamiento total de datos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "codigo_sucursal",
            type=str,
            help="Código único de la sucursal (ej: PUENTE_ALTO, PEDREGAL_PUENTE_ALTO).",
        )
        parser.add_argument(
            "nombre_sucursal",
            type=str,
            help="Nombre formal de la sucursal (ej: 'Pedregal Puente Alto').",
        )
        parser.add_argument(
            "--direccion",
            type=str,
            default="",
            help="Dirección física de la sucursal.",
        )
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Nombre de usuario del operador (por defecto utiliza el código de sucursal).",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Contraseña inicial del operador (si se omite, se generará una segura automáticamente).",
        )
        parser.add_argument(
            "--staff",
            action="store_true",
            help="Habilitar acceso al panel administrativo Django (sin permisos de superusuario).",
        )

    def handle(self, *args, **options):
        codigo = options["codigo_sucursal"].strip()
        nombre = options["nombre_sucursal"].strip()
        direccion = options["direccion"].strip()
        username = options["username"] or codigo
        username = username.strip()
        password = options["password"]
        es_staff = options["staff"]

        if not password:
            password = generar_password_segura(12)

        # 1. Crear o actualizar Sucursal
        sucursal, suc_creada = Sucursal.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre,
                "direccion": direccion,
                "activo": True,
            },
        )
        if not suc_creada:
            sucursal.nombre = nombre
            if direccion:
                sucursal.direccion = direccion
            sucursal.activo = True
            sucursal.save(update_fields=["nombre", "direccion", "activo"])

        # 2. Crear o actualizar Usuario Operador
        User = get_user_model()
        usuario = User.objects.filter(username__iexact=username).first()
        usuario_creado = False

        if not usuario:
            usuario = User.objects.create_user(
                username=username,
                password=password,
                first_name="Operador",
                last_name=nombre,
                is_staff=es_staff,
                is_superuser=False,  # Operadores NUNCA son superusuarios (no pueden crear usuarios)
            )
            usuario_creado = True
        else:
            usuario.set_password(password)
            usuario.is_active = True
            usuario.is_superuser = False
            if es_staff:
                usuario.is_staff = True
            usuario.save(update_fields=["password", "is_active", "is_superuser", "is_staff"])

        # 3. Vincular perfil a la sucursal
        perfil, _ = PerfilUsuario.objects.get_or_create(user=usuario)
        perfil.sucursal = sucursal
        perfil.save(update_fields=["sucursal"])

        # 4. Asegurar configuración de permisos
        configurar_grupos_permisos()

        # Resumen
        self.stdout.write(self.style.SUCCESS("=" * 65))
        self.stdout.write(
            self.style.SUCCESS(
                " SUCURSAL Y OPERADOR CONFIGURADOS EXITOSAMENTE"
            )
        )
        self.stdout.write(self.style.SUCCESS("=" * 65))
        self.stdout.write(f"  [Sucursal]         {sucursal.nombre} ({sucursal.codigo})")
        if sucursal.direccion:
            self.stdout.write(f"  [Direccion]        {sucursal.direccion}")
        self.stdout.write(f"  [Usuario Operador] {usuario.username}")
        self.stdout.write(self.style.WARNING(f"  [Password]         {password}"))
        self.stdout.write(f"  [Alcance]          Operador restringido a '{sucursal.nombre}'")
        self.stdout.write(f"  [Admin Usuarios]   Denegado (exclusivo para Superadministrador)")
        self.stdout.write(self.style.SUCCESS("=" * 65))
        self.stdout.write(
            "El operador podra iniciar sesion en el sistema interno y gestionar "
            "exclusivamente las novedades, colaboradores y periodos de su sede."
        )

