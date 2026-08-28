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

        respuesta_validacion = self.client.post(
            reverse(
                "api:novedad-validar",
                args=[novedad.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            respuesta_validacion.status_code,
            status.HTTP_200_OK,
        )

        novedad.refresh_from_db()
        self.assertEqual(
            novedad.estado,
            Novedad.Estado.VALIDADA,
        )
        self.assertIsNotNone(novedad.validado_en)

        self.assertEqual(
            novedad.validado_por,
            self.usuario,
        )

    def _crear_exportacion_auditoria(self):
        return Exportacion.objects.create(
            periodo=self.periodo,
            generado_por=self.usuario,
            formato=Exportacion.Formato.XLSX,
            nombre_archivo="exportacion_auditoria.xlsx",
            cantidad_registros=1,
        )

    def test_api_permite_consultar_exportaciones(self):
        self.autenticar()
        exportacion = self._crear_exportacion_auditoria()

        respuesta_lista = self.client.get(
            reverse("api:exportacion-list")
        )
        respuesta_detalle = self.client.get(
            reverse(
                "api:exportacion-detail",
                args=[exportacion.pk],
            )
        )

        self.assertEqual(
            respuesta_lista.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            respuesta_detalle.status_code,
            status.HTTP_200_OK,
        )

    def test_api_no_permite_crear_exportaciones_manualmente(self):
        self.autenticar()

        respuesta = self.client.post(
            reverse("api:exportacion-list"),
            {
                "periodo": self.periodo.pk,
                "formato": Exportacion.Formato.XLSX,
                "nombre_archivo": "exportacion_ficticia.xlsx",
                "cantidad_registros": 999,
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertFalse(
            Exportacion.objects.filter(
                nombre_archivo="exportacion_ficticia.xlsx"
            ).exists()
        )

    def test_api_no_permite_reemplazar_exportaciones(self):
        self.autenticar()
        exportacion = self._crear_exportacion_auditoria()

        respuesta = self.client.put(
            reverse(
                "api:exportacion-detail",
                args=[exportacion.pk],
            ),
            {
                "periodo": self.periodo.pk,
                "formato": Exportacion.Formato.CSV,
                "nombre_archivo": "exportacion_alterada.csv",
                "cantidad_registros": 999,
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        exportacion.refresh_from_db()
        self.assertEqual(
            exportacion.nombre_archivo,
            "exportacion_auditoria.xlsx",
        )
        self.assertEqual(exportacion.cantidad_registros, 1)

    def test_api_no_permite_modificar_exportaciones(self):
        self.autenticar()
        exportacion = self._crear_exportacion_auditoria()

        respuesta = self.client.patch(
            reverse(
                "api:exportacion-detail",
                args=[exportacion.pk],
            ),
            {
                "cantidad_registros": 999,
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        exportacion.refresh_from_db()
        self.assertEqual(exportacion.cantidad_registros, 1)

    def test_api_no_permite_eliminar_exportaciones(self):
        self.autenticar()
        exportacion = self._crear_exportacion_auditoria()

        respuesta = self.client.delete(
            reverse(
                "api:exportacion-detail",
                args=[exportacion.pk],
            )
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertTrue(
            Exportacion.objects.filter(
                pk=exportacion.pk
            ).exists()
        )


    def test_api_no_permite_cambiar_estado_directamente(self):
        self.autenticar()

        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            observacion="Novedad ficticia para probar el estado.",
            creado_por=self.usuario,
        )

        respuesta = self.client.patch(
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
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.BORRADOR,
        )
        self.assertIsNone(novedad.validado_por)
        self.assertIsNone(novedad.validado_en)

    def test_api_anular_registra_auditoria(self):
        self.autenticar()

        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            observacion="Novedad ficticia para anular.",
            creado_por=self.usuario,
        )

        motivo = (
            "Registro ficticio anulado mediante la API "
            "para comprobar la auditoría."
        )

        respuesta = self.client.post(
            reverse(
                "api:novedad-anular",
                args=[novedad.pk],
            ),
            {
                "motivo_anulacion": motivo,
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
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

    def test_api_rechaza_motivo_de_anulacion_corto(self):
        self.autenticar()

        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            observacion="Novedad ficticia para probar el motivo.",
            creado_por=self.usuario,
        )

        respuesta = self.client.post(
            reverse(
                "api:novedad-anular",
                args=[novedad.pk],
            ),
            {
                "motivo_anulacion": "Corto",
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "motivo_anulacion",
            respuesta.data,
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.estado,
            Novedad.Estado.BORRADOR,
        )
        self.assertIsNone(novedad.anulado_por)
        self.assertIsNone(novedad.anulado_en)

    def test_api_no_permite_editar_novedad_validada(self):
        self.autenticar()

        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            observacion="Observación inicial ficticia.",
            creado_por=self.usuario,
        )
        novedad.validar(self.usuario)

        respuesta = self.client.patch(
            reverse(
                "api:novedad-detail",
                args=[novedad.pk],
            ),
            {
                "observacion": "Intento de modificación.",
            },
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        novedad.refresh_from_db()

        self.assertEqual(
            novedad.observacion,
            "Observación inicial ficticia.",
        )

    def test_api_no_permite_eliminar_novedades(self):
        self.autenticar()

        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            observacion="Novedad ficticia que no debe eliminarse.",
            creado_por=self.usuario,
        )

        respuesta = self.client.delete(
            reverse(
                "api:novedad-detail",
                args=[novedad.pk],
            )
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertTrue(
            Novedad.objects.filter(pk=novedad.pk).exists()
        )