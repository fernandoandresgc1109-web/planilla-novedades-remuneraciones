from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    AFP,
    Colaborador,
    Exportacion,
    InstitucionSalud,
    Novedad,
    PeriodoLiquidacion,
    Sucursal,
    TipoNovedad,
)


class ApiRestTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_api_prueba",
        )
        cls.sucursal = Sucursal.objects.create(
            codigo="SUC-API",
            nombre="Sucursal API Ficticia",
        )
        cls.afp = AFP.objects.create(
            codigo="AFP-API",
            nombre="AFP API Ficticia",
        )
        cls.institucion_salud = InstitucionSalud.objects.create(
            codigo="SALUD-API",
            nombre="Salud API Ficticia",
            tipo=InstitucionSalud.Tipo.FONASA,
        )
        cls.colaborador = Colaborador.objects.create(
            rut="TESTAPI00001",
            nombres="Nombre API",
            apellidos="Apellido Ficticio",
            sucursal=cls.sucursal,
            afp=cls.afp,
            institucion_salud=cls.institucion_salud,
        )
        cls.periodo = PeriodoLiquidacion.objects.create(
            sucursal=cls.sucursal,
            anio=2026,
            mes=8,
            fecha_inicio=date(2026, 8, 1),
        )
        cls.tipo_novedad = TipoNovedad.objects.create(
            codigo="BONO_API",
            nombre="Bono API Ficticio",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
        )

    def autenticar(self):
        self.client.force_authenticate(user=self.usuario)

    def test_api_rechaza_usuario_no_autenticado(self):
        respuesta = self.client.get(
            reverse("api:sucursal-list")
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_api_root_muestra_diez_endpoints(self):
        self.autenticar()

        respuesta = self.client.get(
            reverse("api:api-root")
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(respuesta.data), 10)
        self.assertIn("novedades", respuesta.data)
        self.assertIn("exportaciones", respuesta.data)

    def test_listado_usa_paginacion(self):
        self.autenticar()

        respuesta = self.client.get(
            reverse("api:sucursal-list")
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(respuesta.data["count"], 1)
        self.assertIn("results", respuesta.data)

    def test_crear_y_validar_novedad_registra_usuario(self):
        self.autenticar()

        respuesta_creacion = self.client.post(
            reverse("api:novedad-list"),
            {
                "periodo": self.periodo.pk,
                "colaborador": self.colaborador.pk,
                "tipo_novedad": self.tipo_novedad.pk,
                "monto": "50000.00",
                "observacion": (
                    "Novedad ficticia creada por la API."
                ),
            },
            format="json",
        )

        self.assertEqual(
            respuesta_creacion.status_code,
            status.HTTP_201_CREATED,
        )

        novedad = Novedad.objects.get(
            pk=respuesta_creacion.data["id"]
        )

        self.assertEqual(
            novedad.creado_por,
            self.usuario,
        )
        self.assertIsNone(novedad.validado_por)

        respuesta_validacion = self.client.patch(
            reverse(
                "api:novedad-detail",
                args=[novedad.pk],
            ),
            {
                "estado": Novedad.Estado.VALIDADA,
            },
            format="json",
        )

        self.assertEqual(
            respuesta_validacion.status_code,
            status.HTTP_200_OK,
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.validado_por,
            self.usuario,
        )

    def test_crear_exportacion_registra_usuario(self):
        self.autenticar()

        respuesta = self.client.post(
            reverse("api:exportacion-list"),
            {
                "periodo": self.periodo.pk,
                "formato": Exportacion.Formato.XLSX,
                "nombre_archivo": (
                    "exportacion_api_ficticia.xlsx"
                ),
                "cantidad_registros": 0,
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )

        exportacion = Exportacion.objects.get(
            pk=respuesta.data["id"]
        )

        self.assertEqual(
            exportacion.generado_por,
            self.usuario,
        )