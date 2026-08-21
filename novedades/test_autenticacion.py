from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccesoInternoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.clave = "ClavePrueba2026!"
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_prueba",
            password=cls.clave,
        )

    def test_pagina_login_responde_correctamente(self):
        respuesta = self.client.get(reverse("login"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "registration/login.html")
        self.assertContains(respuesta, "Iniciar sesión")

    def test_panel_redirige_usuario_no_autenticado(self):
        direccion_panel = reverse("novedades:panel")
        direccion_login = reverse("login")

        respuesta = self.client.get(direccion_panel)

        self.assertRedirects(
            respuesta,
            f"{direccion_login}?next={direccion_panel}",
        )

    def test_usuario_autenticado_puede_acceder_al_panel(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get(reverse("novedades:panel"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "novedades/panel.html")
        self.assertContains(respuesta, "Bienvenido")

    def test_panel_entrega_metricas_iniciales(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get(reverse("novedades:panel"))

        self.assertEqual(respuesta.context["colaboradores_activos"], 0)
        self.assertEqual(respuesta.context["periodos_abiertos"], 0)
        self.assertEqual(respuesta.context["novedades_borrador"], 0)
        self.assertEqual(respuesta.context["novedades_validadas"], 0)

    def test_login_correcto_respeta_direccion_next(self):
        direccion_panel = reverse("novedades:panel")

        respuesta = self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": self.clave,
                "next": direccion_panel,
            },
        )

        self.assertRedirects(respuesta, direccion_panel)

    def test_login_incorrecto_no_inicia_sesion(self):
        respuesta = self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": "clave-incorrecta",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["form"].errors)
        self.assertFalse(
            respuesta.wsgi_request.user.is_authenticated
        )

    def test_cierre_de_sesion_por_post(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.post(reverse("logout"))

        self.assertRedirects(
            respuesta,
            reverse("novedades:inicio"),
        )

        respuesta_panel = self.client.get(
            reverse("novedades:panel")
        )
        self.assertEqual(respuesta_panel.status_code, 302)

    def test_landing_contiene_enlaces_al_panel(self):
        respuesta = self.client.get(reverse("novedades:inicio"))
        enlace_panel = (
            f'href="{reverse("novedades:panel")}"'
        )

        self.assertContains(
            respuesta,
            enlace_panel,
            count=3,
        )