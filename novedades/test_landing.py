from django.templatetags.static import static
from django.test import SimpleTestCase
from django.urls import reverse


class LandingPageTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("novedades:inicio")

    def test_landing_responde_y_utiliza_la_plantilla_correcta(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "novedades/inicio.html")

    def test_landing_explicita_el_proposito_del_proyecto(self):
        respuesta = self.client.get(self.url)

        self.assertContains(
            respuesta,
            "Planilla de Novedades de Remuneraciones",
        )
        self.assertContains(respuesta, "De la novedad al reporte")
        self.assertContains(
            respuesta,
            "Una aplicación diseñada alrededor del proceso real",
        )
        self.assertContains(
            respuesta,
            "Tres etapas para controlar cada período",
        )

    def test_landing_incluye_los_enlaces_principales(self):
        respuesta = self.client.get(self.url)

        self.assertContains(respuesta, 'href="#proyecto"')
        self.assertContains(respuesta, 'href="#solucion"')
        self.assertContains(respuesta, 'href="#flujo"')
        self.assertContains(respuesta, 'href="#tecnologia"')
        self.assertContains(respuesta, 'href="#seguridad"')
        self.assertContains(
            respuesta,
            f'href="{reverse("api:api-root")}"',
        )
        self.assertContains(
            respuesta,
            f'href="{reverse("novedades:panel")}"',
        )

    def test_landing_carga_recursos_y_menu_movil(self):
        respuesta = self.client.get(self.url)

        self.assertContains(
            respuesta,
            static("novedades/css/landing.css"),
        )
        self.assertContains(
            respuesta,
            static("novedades/js/landing.js"),
        )
        self.assertContains(respuesta, "data-menu-button")
        self.assertContains(respuesta, "data-mobile-menu")
        self.assertContains(respuesta, 'aria-expanded="false"')