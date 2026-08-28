from datetime import date
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.html import escape
from rest_framework.test import APIClient

from .models import (
    AFP,
    Banco,
    Colaborador,
    InstitucionSalud,
    Novedad,
    PeriodoLiquidacion,
    Sucursal,
    TipoNovedad,
)

class SeguridadWebTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_seguridad",
            password="ClaveSegura2026!",
        )

    def _cliente_web_csrf_estricto(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        return cliente

    def test_operaciones_web_rechazan_post_sin_csrf(self):
        cliente = self._cliente_web_csrf_estricto()

        rutas_protegidas = (
            reverse("novedades:crear_novedad"),
            reverse(
                "novedades:validar_novedad",
                args=[999],
            ),
            reverse(
                "novedades:anular_novedad",
                args=[999],
            ),
            reverse("novedades:exportar_novedades"),
        )

        for ruta in rutas_protegidas:
            with self.subTest(ruta=ruta):
                respuesta = cliente.post(ruta, {})
                self.assertEqual(respuesta.status_code, 403)

    def test_api_rechaza_post_de_sesion_sin_csrf(self):
        cliente = APIClient(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)

        respuesta = cliente.post(
            reverse("api:sucursal-list"),
            {},
            format="json",
        )

        self.assertEqual(respuesta.status_code, 403)

    def test_formularios_contienen_token_csrf(self):
        respuesta_login = self.client.get(reverse("login"))

        self.assertContains(
            respuesta_login,
            'name="csrfmiddlewaretoken"',
        )

        self.client.force_login(self.usuario)

        rutas_con_formulario = (
            reverse("novedades:crear_novedad"),
            reverse("novedades:exportar_novedades"),
        )

        for ruta in rutas_con_formulario:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(
                    respuesta,
                    'name="csrfmiddlewaretoken"',
                )

    def test_panel_incluye_cabeceras_de_seguridad(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get(
            reverse("novedades:panel")
        )

        self.assertEqual(
            respuesta.headers.get("X-Content-Type-Options"),
            "nosniff",
        )
        self.assertEqual(
            respuesta.headers.get("X-Frame-Options"),
            "DENY",
        )

    def test_paginas_internas_no_se_guardan_en_cache(self):
        self.client.force_login(self.usuario)

        rutas_internas = (
            reverse("novedades:panel"),
            reverse("novedades:lista_novedades"),
            reverse("novedades:crear_novedad"),
            reverse("novedades:exportar_novedades"),
        )

        for ruta in rutas_internas:
            respuesta = self.client.get(ruta)
            cache_control = respuesta.headers.get(
                "Cache-Control",
                "",
            ).lower()

            self.assertIn("no-store", cache_control)

class SeguridadEntradasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_entradas",
            password="ClaveEntradas2026!",
        )

        cls.sucursal = Sucursal.objects.create(
            codigo="SUC-SEG",
            nombre="Sucursal de seguridad",
            direccion="Dirección ficticia",
            activo=True,
        )

        cls.afp = AFP.objects.create(
            codigo="AFP-SEG",
            nombre="AFP de seguridad",
            activo=True,
        )

        cls.salud = InstitucionSalud.objects.create(
            codigo="SALUD-SEG",
            nombre="Salud de seguridad",
            tipo="FONASA",
            activo=True,
        )

        cls.colaborador = Colaborador.objects.create(
            rut="99.999.999-9",
            nombres="Ana",
            apellidos="Seguridad",
            sucursal=cls.sucursal,
            afp=cls.afp,
            institucion_salud=cls.salud,
            cargas_familiares=0,
            seguro_cesantia=True,
            activo=True,
        )

        cls.periodo = PeriodoLiquidacion.objects.create(
            sucursal=cls.sucursal,
            anio=2026,
            mes=8,
            fecha_inicio=date(2026, 8, 1),
            estado=PeriodoLiquidacion.Estado.ABIERTO,
        )

        cls.tipo_novedad = TipoNovedad.objects.create(
            codigo="BONO-SEG",
            nombre="Bono de seguridad",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
            activo=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def _crear_novedad(self, observacion):
        return Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=1000,
            observacion=observacion,
            creado_por=self.usuario,
        )

    def test_xss_almacenado_se_muestra_escapado(self):
        carga_xss = (
            '<script>alert("xss almacenado")</script>'
        )
        novedad = self._crear_novedad(carga_xss)

        respuesta = self.client.get(
            reverse(
                "novedades:editar_novedad",
                args=[novedad.pk],
            )
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, carga_xss)
        self.assertContains(respuesta, escape(carga_xss))

    def test_xss_reflejado_en_busqueda_se_muestra_escapado(self):
        carga_xss = (
            '"><script>alert("xss reflejado")</script>'
        )

        respuesta = self.client.get(
            reverse("novedades:lista_novedades"),
            {"q": carga_xss},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, carga_xss)
        self.assertContains(respuesta, escape(carga_xss))

    def test_busqueda_no_es_vulnerable_a_sql_injection(self):
        self._crear_novedad(
            "Registro legítimo para probar la búsqueda."
        )

        respuesta = self.client.get(
            reverse("novedades:lista_novedades"),
            {"q": "' OR 1=1 --"},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.context["pagina"].paginator.count,
            0,
        )

    def test_api_no_permite_eliminar_catalogos(self):
        catalogos = (
            (
                Sucursal.objects.create(
                    codigo="SUC-DEL",
                    nombre="Sucursal no eliminable",
                    direccion="Dirección ficticia",
                    activo=True,
                ),
                "api:sucursal-detail",
            ),
            (
                Banco.objects.create(
                    codigo="BANCO-DEL",
                    nombre="Banco no eliminable",
                    activo=True,
                ),
                "api:banco-detail",
            ),
            (
                AFP.objects.create(
                    codigo="AFP-DEL",
                    nombre="AFP no eliminable",
                    activo=True,
                ),
                "api:afp-detail",
            ),
            (
                InstitucionSalud.objects.create(
                    codigo="SALUD-DEL",
                    nombre="Salud no eliminable",
                    tipo="FONASA",
                    activo=True,
                ),
                "api:institucion-salud-detail",
            ),
            (
                TipoNovedad.objects.create(
                    codigo="TIPO-DEL",
                    nombre="Tipo no eliminable",
                    unidad_medida=(
                        TipoNovedad.UnidadMedida.PESOS
                    ),
                    naturaleza=TipoNovedad.Naturaleza.HABER,
                    activo=True,
                ),
                "api:tipo-novedad-detail",
            ),
        )

        for catalogo, nombre_ruta in catalogos:
            respuesta = self.client.delete(
                reverse(
                    nombre_ruta,
                    args=[catalogo.pk],
                )
            )

            self.assertEqual(respuesta.status_code, 405)
            self.assertTrue(
                type(catalogo).objects.filter(
                    pk=catalogo.pk
                ).exists()
            )

    def test_admin_no_permite_eliminar_novedades(self):
        usuario_admin = (
            get_user_model().objects.create_superuser(
                username="admin_seguridad",
                password="ClaveAdmin2026!",
            )
        )
        self.client.force_login(usuario_admin)

        novedad = self._crear_novedad(
            "Registro protegido contra eliminación administrativa."
        )

        pagina_cambio = self.client.get(
            reverse(
                "admin:novedades_novedad_change",
                args=[novedad.pk],
            )
        )

        self.assertEqual(pagina_cambio.status_code, 200)
        self.assertNotContains(
            pagina_cambio,
            'class="deletelink"',
        )

        respuesta = self.client.post(
            reverse(
                "admin:novedades_novedad_delete",
                args=[novedad.pk],
            ),
            {"post": "yes"},
        )

        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(
            Novedad.objects.filter(pk=novedad.pk).exists()
        )

    def test_admin_no_permite_eliminar_catalogos(self):
        usuario_admin = (
            get_user_model().objects.create_superuser(
                username="admin_catalogos",
                password="ClaveCatalogos2026!",
            )
        )
        self.client.force_login(usuario_admin)

        banco = Banco.objects.create(
            codigo="BANCO-ADMIN",
            nombre="Banco protegido en administración",
            activo=True,
        )

        catalogos = (
            (self.sucursal, "sucursal"),
            (banco, "banco"),
            (self.afp, "afp"),
            (self.salud, "institucionsalud"),
            (self.tipo_novedad, "tiponovedad"),
        )

        for catalogo, nombre_modelo in catalogos:
            pagina_cambio = self.client.get(
                reverse(
                    (
                        "admin:novedades_"
                        f"{nombre_modelo}_change"
                    ),
                    args=[catalogo.pk],
                )
            )

            self.assertEqual(
                pagina_cambio.status_code,
                200,
            )
            self.assertNotContains(
                pagina_cambio,
                'class="deletelink"',
            )

            respuesta = self.client.post(
                reverse(
                    (
                        "admin:novedades_"
                        f"{nombre_modelo}_delete"
                    ),
                    args=[catalogo.pk],
                ),
                {"post": "yes"},
            )

            self.assertEqual(respuesta.status_code, 403)
            self.assertTrue(
                type(catalogo).objects.filter(
                    pk=catalogo.pk
                ).exists()
            )