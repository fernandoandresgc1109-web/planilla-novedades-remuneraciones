from django.core.management.base import BaseCommand
from novedades.permisos import configurar_grupos_permisos


class Command(BaseCommand):
    help = "Crea o actualiza los grupos de usuarios y sus permisos estándar (Contabilidad, Administrador)."

    def handle(self, *args, **options):
        grupos = configurar_grupos_permisos()
        self.stdout.write(
            self.style.SUCCESS(
                f"Grupos y permisos configurados exitosamente: {', '.join(g.name for g in grupos.values())}"
            )
        )
