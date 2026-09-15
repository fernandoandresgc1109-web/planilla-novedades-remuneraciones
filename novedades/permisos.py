from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

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


def obtener_sucursal_usuario(user):
    """
    Retorna la sucursal asignada al usuario si es un operador de sucursal.
    Los usuarios de Contabilidad y Superadministradores tienen acceso global (retorna None).
    """
    if not user or not user.is_authenticated:
        return None

    # Superusuarios y Contabilidad operan de forma global
    if user.is_superuser or es_usuario_contabilidad(user):
        return None

    # 1. Comprobar perfil de usuario
    try:
        if hasattr(user, "perfil") and user.perfil.sucursal:
            return user.perfil.sucursal
    except Exception:
        pass

    # 2. Resiliencia: buscar coincidencia por username o código de sucursal
    from .models import PerfilUsuario, Sucursal
    username = getattr(user, "username", "").strip()
    if username:
        sucursal = Sucursal.objects.filter(
            activo=True
        ).filter(
            models.Q(codigo__iexact=username)
            | models.Q(nombre__icontains=username.replace("_", " "))
        ).first()

        if sucursal:
            try:
                perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
                if perfil.sucursal != sucursal:
                    perfil.sucursal = sucursal
                    perfil.save(update_fields=["sucursal"])
                return sucursal
            except Exception:
                return sucursal

    return None


def es_usuario_operador_sucursal(user):
    """
    Retorna True si el usuario está restringido operativamente a una única sucursal.
    """
    return obtener_sucursal_usuario(user) is not None


def obtener_sucursales_disponibles(user):
    """
    Retorna el QuerySet de sucursales a las que el usuario tiene acceso.
    - Operador de sucursal: únicamente su sucursal asignada.
    - Contabilidad y Administrador global: todas las sucursales activas.
    """
    from .models import Sucursal

    if not user or not user.is_authenticated:
        return Sucursal.objects.none()

    sucursal_usuario = obtener_sucursal_usuario(user)
    if sucursal_usuario:
        return Sucursal.objects.filter(pk=sucursal_usuario.pk, activo=True)

    return Sucursal.objects.filter(activo=True).order_by("nombre")


def obtener_sucursal_activa(request):
    """
    Determina la sucursal actualmente seleccionada para la sesión:
    - Si el usuario es operador de sucursal: SIEMPRE su sucursal asignada.
    - Si el usuario es global (Admin / Contabilidad): la sucursal almacenada en la sesión
      (o por defecto la primera sucursal activa si aún no se ha seleccionado ninguna).
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None

    # Si es operador de sucursal, no puede alternar
    sucursal_usuario = obtener_sucursal_usuario(user)
    if sucursal_usuario:
        return sucursal_usuario

    from .models import Sucursal

    # Para usuarios globales (Admin / Contabilidad), consultar la sesión
    sucursal_id = request.session.get("sucursal_activa_id")
    if sucursal_id:
        sucursal = Sucursal.objects.filter(pk=sucursal_id, activo=True).first()
        if sucursal:
            return sucursal

    # Valor por defecto: primera sucursal activa
    primera_sucursal = Sucursal.objects.filter(activo=True).order_by("id").first()
    if primera_sucursal:
        request.session["sucursal_activa_id"] = primera_sucursal.pk
        return primera_sucursal

    return None


def cambiar_sucursal_activa(request, sucursal_id):
    """
    Cambia la sucursal activa en la sesión para usuarios con acceso global.
    Los operadores de sucursal no tienen permitido cambiar de sucursal.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False

    if es_usuario_operador_sucursal(user):
        return False

    from .models import Sucursal
    sucursal = Sucursal.objects.filter(pk=sucursal_id, activo=True).first()
    if sucursal:
        request.session["sucursal_activa_id"] = sucursal.pk
        return True

    return False


def puede_administrar_usuarios(user):
    """
    Retorna True si el usuario tiene permisos para crear o gestionar usuarios del sistema.
    Esta función es exclusiva del Superadministrador general.
    Los operadores de sucursal NO pueden crear usuarios.
    """
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser


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

    sucursal_usuario = obtener_sucursal_usuario(user)
    if sucursal_usuario:
        return f"Operador ({sucursal_usuario.nombre})"

    if user.is_superuser:
        return "Superadministrador (Global)"

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
