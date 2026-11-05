from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Sucursal


class AutenticacionApiMovilTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sucursal = Sucursal.objects.create(
            codigo="MOVIL-TEST",
            nombre="Sucursal Móvil Ficticia",
        )
        cls.usuario = get_user_model().objects.create_user(
            username="operador_movil",
            password="ClaveMovilSegura2026!",
            first_name="Usuario",
            last_name="Móvil",
        )
        cls.usuario.perfil.sucursal = cls.sucursal
        cls.usuario.perfil.save(update_fields=["sucursal"])

    def iniciar_sesion(self):
        return self.client.post(
            reverse("api:autenticacion-iniciar"),
            {
                "username": "operador_movil",
                "password": "ClaveMovilSegura2026!",
            },
            format="json",
        )

    def test_inicio_sesion_entrega_token_y_datos_del_operador(self):
        respuesta = self.iniciar_sesion()

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("token", respuesta.data)
        self.assertEqual(
            respuesta.data["usuario"]["username"],
            "operador_movil",
        )
        self.assertEqual(
            respuesta.data["usuario"]["sucursal"]["id"],
            self.sucursal.pk,
        )
        self.assertFalse(respuesta.data["usuario"]["acceso_global"])
        self.assertTrue(respuesta.data["usuario"]["puede_modificar"])

    def test_inicio_sesion_rechaza_credenciales_incorrectas(self):
        respuesta = self.client.post(
            reverse("api:autenticacion-iniciar"),
            {
                "username": "operador_movil",
                "password": "ClaveIncorrecta",
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Token.objects.filter(user=self.usuario).exists())

    def test_token_permite_consultar_usuario_y_api_existente(self):
        token = self.iniciar_sesion().data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        respuesta_usuario = self.client.get(
            reverse("api:autenticacion-usuario")
        )
        respuesta_sucursales = self.client.get(
            reverse("api:sucursal-list")
        )

        self.assertEqual(
            respuesta_usuario.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            respuesta_sucursales.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(respuesta_sucursales.data["count"], 1)
        self.assertEqual(
            respuesta_sucursales.data["results"][0]["id"],
            self.sucursal.pk,
        )

    def test_consulta_usuario_requiere_autenticacion(self):
        respuesta = self.client.get(
            reverse("api:autenticacion-usuario")
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_cierre_sesion_invalida_el_token(self):
        token = self.iniciar_sesion().data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        respuesta_cierre = self.client.post(
            reverse("api:autenticacion-cerrar"),
            {},
            format="json",
        )
        respuesta_posterior = self.client.get(
            reverse("api:autenticacion-usuario")
        )

        self.assertEqual(
            respuesta_cierre.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(Token.objects.filter(user=self.usuario).exists())
        self.assertEqual(
            respuesta_posterior.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
