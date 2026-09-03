from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

NOMBRE_GRUPO_CONTABILIDAD = "Contabilidad"
NOMBRE_GRUPO_ADMINISTRADOR = "Administrador"


def es_usuario_contabilidad(user):
    """
    Retorna True si el usuario autenticado pertenece al rol o grupo de Contabilidad.
    Comprueba el grupo Django, username, nombre, apellido y email (case-insensitive).
    """
    if not user or not user.is_authenticated:
        return False

    # 1. Comprobación por grupo Django
    if user.groups.filter(name__iexact=NOMBRE_GRUPO_CONTABILIDAD).exists():
        return True

    # 2. Comprobación por username, first_name, last_name o email
    username = getattr(user, "username", "").strip().lower()
    first_name = getattr(user, "first_name", "").strip().lower()
    last_name = getattr(user, "last_name", "").strip().lower()
    email = getattr(user, "email", "").strip().lower()

    terminos = ("contabilidad", "contador", "contable", "auditor")
    es_contable = any(
        t in username or t in first_name or t in last_name or t in email
        for t in terminos
    )

    if es_contable:
        try:
            grupo, _ = Group.objects.get_or_create(name=NOMBRE_GRUPO_CONTABILIDAD)
            if not user.groups.filter(pk=grupo.pk).exists():
                user.groups.add(grupo)
        except Exception:
            pass
        return True

    return False


def puede_modificar_novedades(user):
    """
    Retorna True si el usuario tiene autorización para crear, editar, validar o anular novedades.
    El perfil de Contabilidad sólo tiene permisos de visualización y exportación.
    """
    if not user or not user.is_authenticated:
        return False

    # Si es usuario de Contabilidad, SIEMPRE tiene denegada la modificación,
    # incluso si el usuario fue creado con is_superuser=True o is_staff=True.
    if es_usuario_contabilidad(user):
        return False

    if user.is_superuser:
        return True

    return True


def puede_exportar_novedades(user):
    """Retorna True si el usuario está autenticado y tiene autorización para exportar datos."""
    if not user or not user.is_authenticated:
        return False
    return True


def obtener_rol_usuario(user):
    """Retorna una etiqueta descriptiva del rol del usuario activo."""
    if not user or not user.is_authenticated:
        return "Invitado"

    # Prioridad: Contabilidad siempre se identifica como tal
    if es_usuario_contabilidad(user):
        return "Contabilidad (Solo lectura y exportación)"

    if user.is_superuser:
        return "Superadministrador"

    if user.is_staff:
        return "Administrador"

    grupos = list(user.groups.values_list("name", flat=True))
    if grupos:
        return ", ".join(grupos)

    return "Usuario autorizado"


def configurar_grupos_permisos():
    """
    Crea o actualiza los grupos de usuario estándar con sus respectivos permisos en Django.
    """
    grupo_contabilidad, _ = Group.objects.get_or_create(
        name=NOMBRE_GRUPO_CONTABILIDAD
    )

    from .models import (
        AFP,
        Banco,
        Colaborador,
        Contrato,
        Exportacion,
        InstitucionSalud,
        Novedad,
        PeriodoLiquidacion,
        Sucursal,
        TipoNovedad,
    )

    modelos_lectura = [
        Sucursal,
        Banco,
        AFP,
        InstitucionSalud,
        Colaborador,
        Contrato,
        PeriodoLiquidacion,
        TipoNovedad,
        Novedad,
        Exportacion,
    ]

    permisos_contabilidad = []
    for modelo in modelos_lectura:
        ct = ContentType.objects.get_for_model(modelo)
        permiso_view = Permission.objects.filter(
            content_type=ct, codename=f"view_{modelo._meta.model_name}"
        ).first()
        if permiso_view:
            permisos_contabilidad.append(permiso_view)

    ct_export = ContentType.objects.get_for_model(Exportacion)
    permiso_add_export = Permission.objects.filter(
        content_type=ct_export, codename="add_exportacion"
    ).first()
    if permiso_add_export:
        permisos_contabilidad.append(permiso_add_export)

    grupo_contabilidad.permissions.set(permisos_contabilidad)

    grupo_admin, _ = Group.objects.get_or_create(
        name=NOMBRE_GRUPO_ADMINISTRADOR
    )
    permisos_admin = []
    for modelo in modelos_lectura:
        ct = ContentType.objects.get_for_model(modelo)
        perms = Permission.objects.filter(content_type=ct)
        permisos_admin.extend(perms)

    grupo_admin.permissions.set(permisos_admin)

    # Asignar automáticamente usuarios cuyo username sea 'contabilidad'
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        usuarios_contables = User.objects.filter(username__icontains="contabilidad")
        for u in usuarios_contables:
            u.groups.add(grupo_contabilidad)
    except Exception:
        pass

    return {
        "contabilidad": grupo_contabilidad,
        "administrador": grupo_admin,
    }
