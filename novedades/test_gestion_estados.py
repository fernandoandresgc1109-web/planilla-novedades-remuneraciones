from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import (
    AFP,
    Colaborador,
    InstitucionSalud,
    Novedad,
    PeriodoLiquidacion,
    Sucursal,
    TipoNovedad,
)


class GestionEstadosNovedadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="gestor_estados_prueba",
            password="ClaveSegura123!",
        )

        cls.sucursal = Sucursal.objects.create(
            codigo="SUC-ESTADOS",
            nombre="Sucursal estados",
            direccion="Dirección completamente ficticia",
            activo=True,
        )

        cls.afp = AFP.objects.create(
            codigo="AFP-ESTADOS",
            nombre="AFP estados",
            activo=True,
        )

        cls.salud = InstitucionSalud.objects.create(
            codigo="SALUD-ESTADOS",
            nombre="Salud estados",
            tipo="FONASA",
            activo=True,
        )

        cls.colaborador = Colaborador.objects.create(
            rut="88.888.888-8",
            nombres="Laura",
            apellidos="Ficticia",
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
            codigo="BONO-ESTADOS",
            nombre="Bono estados",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
            activo=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def crear_novedad(self):
        return Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=Decimal("50000"),
            observacion="Registro completamente ficticio.",
            creado_por=self.usuario,
        )

    def test_rutas_de_gestion_requieren_autenticacion(self):
        novedad = self.crear_novedad()
        self.client.logout()

        rutas_get = [
            reverse(
                "novedades:editar_novedad",
                args=[novedad.pk],
            ),
            reverse(
                "novedades:anular_novedad",
                args=[novedad.pk],
            ),
        ]

        for ruta in rutas_get:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)

                self.assertRedirects(
                    respuesta,
                    f"{reverse('login')}?next={ruta}",
                )

        ruta_validacion = reverse(
            "novedades:validar_novedad",
            args=[novedad.pk],
        )
        respuesta = self.client.post(ruta_validacion)

        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={ruta_validacion}",
        )

    def test_borrador_permite_editar_validar_y_anular(self):
        novedad = self.crear_novedad()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.BORRADOR,
        )
        self.assertTrue(novedad.puede_editar)
        self.assertTrue(novedad.puede_validar)
        self.assertTrue(novedad.puede_anular)

    def test_validar_registra_estado_usuario_y_fecha(self):
        novedad = self.crear_novedad()

        respuesta = self.client.post(
            reverse(
                "novedades:validar_novedad",
                args=[novedad.pk],
            )
        )

        self.assertRedirects(
            respuesta,
            reverse("novedades:lista_novedades"),
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.VALIDADA,
        )
        self.assertEqual(
            novedad.validado_por,
            self.usuario,
        )
        self.assertIsNotNone(novedad.validado_en)
        self.assertFalse(novedad.puede_editar)
        self.assertFalse(novedad.puede_validar)
        self.assertTrue(novedad.puede_anular)

    def test_validacion_solo_acepta_post(self):
        novedad = self.crear_novedad()

        respuesta = self.client.get(
            reverse(
                "novedades:validar_novedad",
                args=[novedad.pk],
            )
        )

        self.assertEqual(respuesta.status_code, 405)

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.BORRADOR,
        )

    def test_novedad_validada_no_se_puede_editar(self):
        novedad = self.crear_novedad()
        novedad.validar(self.usuario)

        respuesta = self.client.get(
            reverse(
                "novedades:editar_novedad",
                args=[novedad.pk],
            )
        )

        self.assertRedirects(
            respuesta,
            reverse("novedades:lista_novedades"),
        )

    def test_anular_registra_motivo_usuario_y_fecha(self):
        novedad = self.crear_novedad()
        novedad.validar(self.usuario)

        motivo = (
            "Registro ficticio anulado para comprobar "
            "la trazabilidad."
        )

        respuesta = self.client.post(
            reverse(
                "novedades:anular_novedad",
                args=[novedad.pk],
            ),
            {
                "motivo_anulacion": motivo,
            },
        )

        self.assertRedirects(
            respuesta,
            reverse("novedades:lista_novedades"),
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.ANULADA,
        )
        self.assertEqual(
            novedad.anulado_por,
            self.usuario,
        )
        self.assertIsNotNone(novedad.anulado_en)
        self.assertEqual(
            novedad.motivo_anulacion,
            motivo,
        )
        self.assertFalse(novedad.puede_editar)
        self.assertFalse(novedad.puede_validar)
        self.assertFalse(novedad.puede_anular)

        respuesta_listado = self.client.get(
            reverse("novedades:lista_novedades")
        )

        self.assertContains(
            respuesta_listado,
            motivo,
        )

    def test_anulacion_rechaza_motivo_demasiado_corto(self):
        novedad = self.crear_novedad()

        respuesta = self.client.post(
            reverse(
                "novedades:anular_novedad",
                args=[novedad.pk],
            ),
            {
                "motivo_anulacion": "Corto",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(
            "motivo_anulacion",
            respuesta.context["formulario"].errors,
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.BORRADOR,
        )
        self.assertIsNone(novedad.anulado_por)
        self.assertIsNone(novedad.anulado_en)

    def test_novedad_anulada_no_admite_nuevas_transiciones(self):
        novedad = self.crear_novedad()

        novedad.anular(
            self.usuario,
            "Motivo ficticio suficientemente detallado.",
        )

        with self.assertRaises(ValidationError):
            novedad.validar(self.usuario)

        with self.assertRaises(ValidationError):
            novedad.anular(
                self.usuario,
                "Segundo intento ficticio de anulación.",
            )