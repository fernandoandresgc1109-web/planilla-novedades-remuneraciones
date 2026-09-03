from .permisos import (
    es_usuario_contabilidad,
    obtener_rol_usuario,
    puede_exportar_novedades,
    puede_modificar_novedades,
)


def permisos_usuario(request):
    """
    Inyecta información de permisos y rol del usuario activo en todas las plantillas.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {
            "es_contabilidad": False,
            "puede_modificar": False,
            "puede_exportar": False,
            "rol_usuario": "Invitado",
        }

    return {
        "es_contabilidad": es_usuario_contabilidad(user),
        "puede_modificar": puede_modificar_novedades(user),
        "puede_exportar": puede_exportar_novedades(user),
        "rol_usuario": obtener_rol_usuario(user),
    }
