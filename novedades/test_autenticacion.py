from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import Resolver404, resolve, reverse


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

    def test_login_rechaza_redireccion_a_dominio_externo(self):
        respuesta = self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": self.clave,
                "next": (
                    "https://sitio-malicioso.example/"
                    "robar-sesion"
                ),
            },
        )

        self.assertRedirects(
            respuesta,
            reverse("novedades:panel"),
        )

    def test_logout_no_acepta_get(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get(reverse("logout"))

        self.assertEqual(respuesta.status_code, 405)

        respuesta_panel = self.client.get(
            reverse("novedades:panel")
        )
        self.assertEqual(respuesta_panel.status_code, 200)

    def test_login_rechaza_post_sin_token_csrf(self):
        cliente_csrf = Client(enforce_csrf_checks=True)

        respuesta = cliente_csrf.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": self.clave,
            },
        )

        self.assertEqual(respuesta.status_code, 403)

    def test_logout_rechaza_post_sin_token_csrf(self):
        cliente_csrf = Client(enforce_csrf_checks=True)
        cliente_csrf.force_login(self.usuario)

        respuesta = cliente_csrf.post(reverse("logout"))

        self.assertEqual(respuesta.status_code, 403)

    def test_rutas_de_clave_no_implementadas_no_se_exponen(self):
        rutas_no_implementadas = (
            "/cuentas/password_reset/",
            "/cuentas/password_reset/done/",
            "/cuentas/reset/usuario/token/",
            "/cuentas/reset/done/",
        )

        for ruta in rutas_no_implementadas:
            with self.assertRaises(Resolver404):
                resolve(ruta)

    def test_pagina_cambio_clave_requiere_autenticacion(self):
        respuesta = self.client.get(reverse("password_change"))
        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={reverse('password_change')}",
        )

    def test_pagina_cambio_clave_responde_a_usuario_autenticado(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse("password_change"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "registration/password_change_form.html",
        )
        self.assertContains(respuesta, "Cambiar contraseña")

    def test_cambio_clave_exitoso(self):
        self.client.force_login(self.usuario)
        nueva_clave = "NuevaClavePersonal2026!"

        respuesta = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.clave,
                "new_password1": nueva_clave,
                "new_password2": nueva_clave,
            },
        )

        self.assertRedirects(respuesta, reverse("password_change_done"))
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(nueva_clave))

        # Verificar acceso a la página de confirmación
        respuesta_done = self.client.get(reverse("password_change_done"))
        self.assertEqual(respuesta_done.status_code, 200)
        self.assertTemplateUsed(
            respuesta_done,
            "registration/password_change_done.html",
        )

    def test_comando_reset_clave(self):
        from django.core.management import call_command
        clave_temporal = "TemporalSegura2026!"

        call_command(
            "reset_clave",
            self.usuario.username,
            password=clave_temporal,
        )

        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(clave_temporal))

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