from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permisos import (
    obtener_rol_usuario,
    obtener_sucursal_usuario,
    puede_exportar_novedades,
    puede_modificar_novedades,
)


def construir_datos_usuario(user):
    """Prepara la información mínima que necesita el cliente móvil."""
    sucursal = obtener_sucursal_usuario(user)

    return {
        "id": user.pk,
        "username": user.get_username(),
        "nombre": user.get_full_name().strip(),
        "rol": obtener_rol_usuario(user),
        "sucursal": (
            {
                "id": sucursal.pk,
                "codigo": sucursal.codigo,
                "nombre": sucursal.nombre,
            }
            if sucursal
            else None
        ),
        "acceso_global": sucursal is None,
        "puede_modificar": puede_modificar_novedades(user),
        "puede_exportar": puede_exportar_novedades(user),
    }


class InicioSesionMovilAPIView(ObtainAuthToken):
    """Valida las credenciales y entrega un token al cliente Android."""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "usuario": construir_datos_usuario(user),
            }
        )


class UsuarioActualMovilAPIView(APIView):
    """Permite que la aplicación recupere el usuario y sus permisos."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            {"usuario": construir_datos_usuario(request.user)}
        )


class CerrarSesionMovilAPIView(APIView):
    """Invalida el token presentado en la solicitud."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if isinstance(request.auth, Token):
            request.auth.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
