import secrets
import string
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from novedades.permisos import NOMBRE_GRUPO_CONTABILIDAD, configurar_grupos_permisos


def generar_password_segura(longitud=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    # Garantizar al menos una mayúscula, una minúscula, un dígito y un símbolo
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
        "Restablece o asigna una contraseña a un usuario (útil para contraseñas "
        "temporales, olvidos o cambio de encargado)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="Nombre de usuario al que se le cambiará la contraseña.",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Nueva contraseña (si se omite, se generará una contraseña temporal aleatoria).",
        )
        parser.add_argument(
            "--crear",
            action="store_true",
            help="Crear el usuario si no existe en la base de datos.",
        )

    def handle(self, *args, **options):
        username = options["username"].strip()
        nueva_clave = options["password"]
        crear_si_no_existe = options["crear"]

        if not nueva_clave:
            nueva_clave = generar_password_segura(12)

        User = get_user_model()
        usuario = User.objects.filter(username__iexact=username).first()

        if not usuario:
            if crear_si_no_existe or username.lower() == "contabilidad":
                usuario = User.objects.create_user(
                    username=username,
                    password=nueva_clave,
                    first_name="Encargado",
                    last_name="Contabilidad",
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Usuario '{username}' creado exitosamente.")
                )
            else:
                raise CommandError(
                    f"El usuario '{username}' no existe. Usa el flag --crear si deseas crearlo."
                )
        else:
            usuario.set_password(nueva_clave)
            usuario.is_active = True
            usuario.save(update_fields=["password", "is_active"])

        # Asegurar configuración de grupos
        configurar_grupos_permisos()

        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS(f" Contraseña restablecida para: {usuario.username}")
        )
        self.stdout.write(
            self.style.WARNING(f" Nueva contraseña temporal:   {nueva_clave}")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            "El usuario puede ingresar con esta clave y luego ir a 'Cambiar contraseña' "
            "para establecer su propia clave secreta."
        )
