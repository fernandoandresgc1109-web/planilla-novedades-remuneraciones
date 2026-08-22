from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
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


class CapturaNovedadesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="operador_prueba",
            password="ClaveSegura123!",
        )

        cls.sucursal = Sucursal.objects.create(
            codigo="SUC-PRUEBA",
            nombre="Sucursal de prueba",
            direccion="Dirección ficticia",
            activo=True,
        )

        cls.afp = AFP.objects.create(
            codigo="AFP-PRUEBA",
            nombre="AFP de prueba",
            activo=True,
        )

        cls.salud = InstitucionSalud.objects.create(
            codigo="SALUD-PRUEBA",
            nombre="Salud de prueba",
            tipo="FONASA",
            activo=True,
        )

        cls.colaborador = Colaborador.objects.create(
            rut="99.999.999-9",
            nombres="Ana",
            apellidos="Demostración",
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

        cls.tipo_bono = TipoNovedad.objects.create(
            codigo="BONO-PRUEBA",
            nombre="Bono de prueba",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
            activo=True,
        )

        cls.tipo_horas = TipoNovedad.objects.create(
            codigo="HORAS-PRUEBA",
            nombre="Horas extras de prueba",
            unidad_medida=TipoNovedad.UnidadMedida.MINUTOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
            activo=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def datos_formulario(self, tipo_novedad):
        return {
            "periodo": self.periodo.pk,
            "colaborador": self.colaborador.pk,
            "tipo_novedad": tipo_novedad.pk,
            "fecha_inicio": "",
            "fecha_termino": "",
            "cantidad": "",
            "monto": "",
            "observacion": "Información completamente ficticia.",
        }

    def test_rutas_requieren_autenticacion(self):
        self.client.logout()

        rutas = [
            reverse("novedades:lista_novedades"),
            reverse("novedades:crear_novedad"),
        ]

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)

                self.assertRedirects(
                    respuesta,
                    f"{reverse('login')}?next={ruta}",
                )

    def test_formulario_muestra_opciones_habilitadas(self):
        respuesta = self.client.get(
            reverse("novedades:crear_novedad")
        )

        self.assertEqual(respuesta.status_code, 200)

        formulario = respuesta.context["formulario"]

        self.assertIn(
            self.periodo,
            formulario.fields["periodo"].queryset,
        )
        self.assertIn(
            self.colaborador,
            formulario.fields["colaborador"].queryset,
        )
        self.assertIn(
            self.tipo_bono,
            formulario.fields["tipo_novedad"].queryset,
        )

    def test_bono_sin_monto_es_rechazado(self):
        datos = self.datos_formulario(self.tipo_bono)

        respuesta = self.client.post(
            reverse("novedades:crear_novedad"),
            datos,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(
            "monto",
            respuesta.context["formulario"].errors,
        )
        self.assertEqual(Novedad.objects.count(), 0)

    def test_horas_extra_sin_cantidad_son_rechazadas(self):
        datos = self.datos_formulario(self.tipo_horas)

        respuesta = self.client.post(
            reverse("novedades:crear_novedad"),
            datos,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(
            "cantidad",
            respuesta.context["formulario"].errors,
        )
        self.assertEqual(Novedad.objects.count(), 0)

    def test_registro_valido_guarda_usuario_y_estado(self):
        datos = self.datos_formulario(self.tipo_bono)
        datos["monto"] = "50000"

        respuesta = self.client.post(
            reverse("novedades:crear_novedad"),
            datos,
        )

        self.assertRedirects(
            respuesta,
            reverse("novedades:lista_novedades"),
        )

        novedad = Novedad.objects.get()

        self.assertEqual(novedad.creado_por, self.usuario)
        self.assertEqual(
            novedad.estado,
            Novedad.Estado.BORRADOR,
        )
        self.assertEqual(
            novedad.monto,
            Decimal("50000"),
        )

    def test_listado_busca_y_filtra_registros(self):
        Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_bono,
            monto=Decimal("50000"),
            estado=Novedad.Estado.BORRADOR,
            creado_por=self.usuario,
        )

        respuesta = self.client.get(
            reverse("novedades:lista_novedades"),
            {
                "q": "ana",
                "estado": Novedad.Estado.BORRADOR,
                "periodo": self.periodo.pk,
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.context["pagina"].paginator.count,
            1,
        )
        self.assertContains(respuesta, "Ana")
        self.assertContains(respuesta, "Demostración")
        self.assertContains(respuesta, "Bono de prueba")