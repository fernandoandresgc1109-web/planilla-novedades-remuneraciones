from django.test import SimpleTestCase
from django.urls import reverse


class PaginaInicioTests(SimpleTestCase):
    def test_pagina_inicio_responde_correctamente(self):
        respuesta = self.client.get(reverse("novedades:inicio"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "Planilla de Novedades de Remuneraciones",
        )