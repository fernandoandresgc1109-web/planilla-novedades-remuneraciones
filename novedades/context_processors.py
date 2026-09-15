from .permisos import (
    es_usuario_contabilidad,
    es_usuario_operador_sucursal,
    obtener_rol_usuario,
    obtener_sucursal_activa,
    obtener_sucursales_disponibles,
    puede_administrar_usuarios,
    puede_exportar_novedades,
    puede_modificar_novedades,
)


def permisos_usuario(request):
    """
    Inyecta información de permisos, rol y sucursal activa del usuario en todas las plantillas.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {
            "es_contabilidad": False,
            "puede_modificar": False,
            "puede_exportar": False,
            "puede_administrar_usuarios": False,
            "es_usuario_sucursal": False,
            "puede_cambiar_sucursal": False,
            "rol_usuario": "Invitado",
            "sucursal_activa": None,
            "sucursales_disponibles": [],
            "nombre_sucursal_activa": "Sin sucursal",
        }

    sucursal_activa = obtener_sucursal_activa(request)
    sucursales_disponibles = list(obtener_sucursales_disponibles(user))
    es_op_sucursal = es_usuario_operador_sucursal(user)

    return {
        "es_contabilidad": es_usuario_contabilidad(user),
        "puede_modificar": puede_modificar_novedades(user),
        "puede_exportar": puede_exportar_novedades(user),
        "puede_administrar_usuarios": puede_administrar_usuarios(user),
        "es_usuario_sucursal": es_op_sucursal,
        "puede_cambiar_sucursal": (not es_op_sucursal) and len(sucursales_disponibles) > 1,
        "rol_usuario": obtener_rol_usuario(user),
        "sucursal_activa": sucursal_activa,
        "sucursales_disponibles": sucursales_disponibles,
        "nombre_sucursal_activa": (
            sucursal_activa.nombre if sucursal_activa else "Todas las sucursales"
        ),
    }

