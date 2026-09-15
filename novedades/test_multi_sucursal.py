from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from novedades.models import (
    AFP,
    Banco,
    Colaborador,
    Contrato,
    Exportacion,
    InstitucionSalud,
    Novedad,
    PerfilUsuario,
    PeriodoLiquidacion,
    Sucursal,
    TipoNovedad,
)
from novedades.permisos import (
    es_usuario_operador_sucursal,
    obtener_sucursal_usuario,
    puede_administrar_usuarios,
    puede_modificar_novedades,
)

User = get_user_model()


class MultiSucursalIsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 1. Catálogos base
        cls.banco = Banco.objects.create(codigo="BCH", nombre="Banco de Chile")
        cls.afp = AFP.objects.create(codigo="HABITAT", nombre="AFP Habitat")
        cls.salud = InstitucionSalud.objects.create(
            codigo="FONASA",
            nombre="FONASA",
            tipo=InstitucionSalud.Tipo.FONASA,
        )
        cls.tipo_bono = TipoNovedad.objects.create(
            codigo="BONO_PROD",
            nombre="Bono de Producción",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
        )
        cls.tipo_dias = TipoNovedad.objects.create(
            codigo="DIAS_LIC",
            nombre="Días de Licencia",
            unidad_medida=TipoNovedad.UnidadMedida.DIAS,
            naturaleza=TipoNovedad.Naturaleza.DESCUENTO,
        )

        # 2. Sucursales
        cls.sucursal_rancagua = Sucursal.objects.create(
            codigo="RANCAGUA",
            nombre="Alimentos Rancagua SpA",
            direccion="Av. Central 100, Rancagua",
        )
        cls.sucursal_pedregal = Sucursal.objects.create(
            codigo="PEDREGAL_PUENTE_ALTO",
            nombre="Pedregal Puente Alto",
            direccion="Av. Concha y Toro 500, Puente Alto",
        )

        # 3. Usuarios
        cls.admin_global = User.objects.create_superuser(
            username="admin_global",
            password="AdminPassword2026!",
            email="admin@alimentosrancagua.cl",
        )

        cls.user_contabilidad = User.objects.create_user(
            username="contabilidad",
            password="ContaPassword2026!",
            first_name="Encargado",
            last_name="Contabilidad",
        )

        cls.user_pedregal = User.objects.create_user(
            username="PEDREGAL_PUENTE_ALTO",
            password="PedregalPassword2026!",
            first_name="Operador",
            last_name="Puente Alto",
        )
        cls.user_pedregal.perfil.sucursal = cls.sucursal_pedregal
        cls.user_pedregal.perfil.save()

        # 4. Colaboradores por sucursal
        cls.colab_rancagua = Colaborador.objects.create(
            rut="11.111.111-1",
            nombres="Juan",
            apellidos="Pérez Rancagua",
            sucursal=cls.sucursal_rancagua,
            banco=cls.banco,
            numero_cuenta="123456",
            tipo_cuenta=Colaborador.TipoCuenta.CORRIENTE,
            afp=cls.afp,
            institucion_salud=cls.salud,
        )

        cls.colab_pedregal = Colaborador.objects.create(
            rut="22.222.222-2",
            nombres="María",
            apellidos="González Puente Alto",
            sucursal=cls.sucursal_pedregal,
            banco=cls.banco,
            numero_cuenta="654321",
            tipo_cuenta=Colaborador.TipoCuenta.VISTA,
            afp=cls.afp,
            institucion_salud=cls.salud,
        )

        # 5. Períodos por sucursal
        cls.periodo_rancagua = PeriodoLiquidacion.objects.create(
            sucursal=cls.sucursal_rancagua,
            anio=2026,
            mes=9,
            fecha_inicio=date(2026, 9, 1),
            estado=PeriodoLiquidacion.Estado.ABIERTO,
        )

        cls.periodo_pedregal = PeriodoLiquidacion.objects.create(
            sucursal=cls.sucursal_pedregal,
            anio=2026,
            mes=9,
            fecha_inicio=date(2026, 9, 1),
            estado=PeriodoLiquidacion.Estado.ABIERTO,
        )

        # 6. Novedades por sucursal
        cls.novedad_rancagua = Novedad.objects.create(
            periodo=cls.periodo_rancagua,
            colaborador=cls.colab_rancagua,
            tipo_novedad=cls.tipo_bono,
            monto=Decimal("75000"),
            estado=Novedad.Estado.BORRADOR,
            creado_por=cls.admin_global,
        )

        cls.novedad_pedregal = Novedad.objects.create(
            periodo=cls.periodo_pedregal,
            colaborador=cls.colab_pedregal,
            tipo_novedad=cls.tipo_bono,
            monto=Decimal("50000"),
            estado=Novedad.Estado.BORRADOR,
            creado_por=cls.user_pedregal,
        )

    # -------------------------------------------------------------
    # 1. PERMISOS Y ROLES
    # -------------------------------------------------------------
    def test_perfil_usuario_se_crea_automaticamente(self):
        nuevo_user = User.objects.create_user(username="nuevo_test", password="pw")
        self.assertTrue(hasattr(nuevo_user, "perfil"))
        self.assertIsNone(nuevo_user.perfil.sucursal)

    def test_roles_y_asignacion_sucursal(self):
        # Operador de sucursal
        self.assertEqual(
            obtener_sucursal_usuario(self.user_pedregal),
            self.sucursal_pedregal,
        )
        self.assertTrue(es_usuario_operador_sucursal(self.user_pedregal))
        self.assertFalse(puede_administrar_usuarios(self.user_pedregal))
        self.assertTrue(puede_modificar_novedades(self.user_pedregal))

        # Contabilidad (Global)
        self.assertIsNone(obtener_sucursal_usuario(self.user_contabilidad))
        self.assertFalse(es_usuario_operador_sucursal(self.user_contabilidad))
        self.assertFalse(puede_administrar_usuarios(self.user_contabilidad))
        self.assertFalse(puede_modificar_novedades(self.user_contabilidad))

        # Administrador (Global)
        self.assertIsNone(obtener_sucursal_usuario(self.admin_global))
        self.assertFalse(es_usuario_operador_sucursal(self.admin_global))
        self.assertTrue(puede_administrar_usuarios(self.admin_global))
        self.assertTrue(puede_modificar_novedades(self.admin_global))

    # -------------------------------------------------------------
    # 2. MANAGEMENT COMMAND: crear_sucursal_operador
    # -------------------------------------------------------------
    def test_comando_crear_sucursal_operador(self):
        call_command(
            "crear_sucursal_operador",
            "VALPARAISO",
            "Sucursal Valparaíso",
            direccion="Calle Prat 123",
            username="OPERADOR_VALPARAISO",
            password="ValpoPassword2026!",
        )

        sucursal = Sucursal.objects.get(codigo="VALPARAISO")
        self.assertEqual(sucursal.nombre, "Sucursal Valparaíso")

        usuario = User.objects.get(username="OPERADOR_VALPARAISO")
        self.assertFalse(usuario.is_superuser)
        self.assertTrue(usuario.check_password("ValpoPassword2026!"))
        self.assertEqual(usuario.perfil.sucursal, sucursal)

    # -------------------------------------------------------------
    # 3. AISLAMIENTO OPERADOR EN VISTAS WEB
    # -------------------------------------------------------------
    def test_operador_panel_solo_cuenta_datos_de_su_sucursal(self):
        self.client.force_login(self.user_pedregal)
        res = self.client.get(reverse("novedades:panel"))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["colaboradores_activos"], 1)  # Solo colab_pedregal
        self.assertEqual(res.context["periodos_abiertos"], 1)      # Solo periodo_pedregal
        self.assertEqual(res.context["novedades_borrador"], 1)     # Solo novedad_pedregal
        self.assertEqual(res.context["sucursal_activa"], self.sucursal_pedregal)

    def test_operador_lista_novedades_solo_ve_su_sucursal(self):
        self.client.force_login(self.user_pedregal)
        res = self.client.get(reverse("novedades:lista_novedades"))

        self.assertEqual(res.status_code, 200)
        novedades_mostradas = list(res.context["pagina"].object_list)
        self.assertIn(self.novedad_pedregal, novedades_mostradas)
        self.assertNotIn(self.novedad_rancagua, novedades_mostradas)

    def test_operador_bloqueado_de_editar_novedad_otra_sucursal(self):
        self.client.force_login(self.user_pedregal)
        # Intentar acceder a la novedad de Rancagua
        res = self.client.get(
            reverse("novedades:editar_novedad", args=[self.novedad_rancagua.pk])
        )
        self.assertEqual(res.status_code, 404)

    def test_operador_bloqueado_de_validar_novedad_otra_sucursal(self):
        self.client.force_login(self.user_pedregal)
        res = self.client.post(
            reverse("novedades:validar_novedad", args=[self.novedad_rancagua.pk])
        )
        self.assertEqual(res.status_code, 404)
        self.novedad_rancagua.refresh_from_db()
        self.assertEqual(self.novedad_rancagua.estado, Novedad.Estado.BORRADOR)

    def test_operador_bloqueado_de_anular_novedad_otra_sucursal(self):
        self.client.force_login(self.user_pedregal)
        res = self.client.post(
            reverse("novedades:anular_novedad", args=[self.novedad_rancagua.pk]),
            {"motivo_anulacion": "Motivo de prueba con suficiente longitud"},
        )
        self.assertEqual(res.status_code, 404)
        self.novedad_rancagua.refresh_from_db()
        self.assertEqual(self.novedad_rancagua.estado, Novedad.Estado.BORRADOR)

    def test_operador_formulario_crear_novedad_solo_lista_opciones_de_su_sucursal(self):
        self.client.force_login(self.user_pedregal)
        res = self.client.get(reverse("novedades:crear_novedad"))

        self.assertEqual(res.status_code, 200)
        periodos_form = list(res.context["formulario"].fields["periodo"].queryset)
        colaboradores_form = list(res.context["formulario"].fields["colaborador"].queryset)

        self.assertIn(self.periodo_pedregal, periodos_form)
        self.assertNotIn(self.periodo_rancagua, periodos_form)

        self.assertIn(self.colab_pedregal, colaboradores_form)
        self.assertNotIn(self.colab_rancagua, colaboradores_form)

    def test_operador_no_puede_cambiar_de_sucursal(self):
        self.client.force_login(self.user_pedregal)
        res = self.client.post(
            reverse("novedades:cambiar_sucursal"),
            {"sucursal_id": self.sucursal_rancagua.pk},
        )
        self.assertRedirects(res, reverse("novedades:panel"))

        # El operador sigue en su sede
        res_panel = self.client.get(reverse("novedades:panel"))
        self.assertEqual(res_panel.context["sucursal_activa"], self.sucursal_pedregal)

    # -------------------------------------------------------------
    # 4. CONTABILIDAD: MULTI-SUCURSAL Y CAMBIO DE SEDE
    # -------------------------------------------------------------
    def test_contabilidad_puede_cambiar_de_sucursal_y_ver_por_separado(self):
        self.client.force_login(self.user_contabilidad)

        # 1. Cambiar a Sucursal Rancagua
        res_cambio1 = self.client.post(
            reverse("novedades:cambiar_sucursal"),
            {"sucursal_id": self.sucursal_rancagua.pk},
        )
        self.assertRedirects(res_cambio1, reverse("novedades:panel"))

        res_lista1 = self.client.get(reverse("novedades:lista_novedades"))
        novedades_rancagua = list(res_lista1.context["pagina"].object_list)
        self.assertIn(self.novedad_rancagua, novedades_rancagua)
        self.assertNotIn(self.novedad_pedregal, novedades_rancagua)

        # 2. Cambiar a Sucursal Pedregal
        res_cambio2 = self.client.post(
            reverse("novedades:cambiar_sucursal"),
            {"sucursal_id": self.sucursal_pedregal.pk},
        )
        self.assertRedirects(res_cambio2, reverse("novedades:panel"))

        res_lista2 = self.client.get(reverse("novedades:lista_novedades"))
        novedades_pedregal = list(res_lista2.context["pagina"].object_list)
        self.assertIn(self.novedad_pedregal, novedades_pedregal)
        self.assertNotIn(self.novedad_rancagua, novedades_pedregal)

    def test_contabilidad_puede_exportar_excel_por_sucursal_separada(self):
        # Validar novedad de Pedregal para que sea exportable
        self.novedad_pedregal.validar(self.admin_global)

        self.client.force_login(self.user_contabilidad)
        self.client.post(
            reverse("novedades:cambiar_sucursal"),
            {"sucursal_id": self.sucursal_pedregal.pk},
        )

        res_export = self.client.post(
            reverse("novedades:exportar_novedades"),
            {
                "periodo": self.periodo_pedregal.pk,
                "formato": Exportacion.Formato.XLSX,
            },
        )

        self.assertEqual(res_export.status_code, 200)
        self.assertEqual(
            res_export["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("pedregal_puente_alto", res_export["Content-Disposition"].lower())

    def test_contabilidad_sigue_bloqueado_de_crear_novedad_en_cualquier_sucursal(self):
        self.client.force_login(self.user_contabilidad)
        res = self.client.post(
            reverse("novedades:crear_novedad"),
            {
                "periodo": self.periodo_pedregal.pk,
                "colaborador": self.colab_pedregal.pk,
                "tipo_novedad": self.tipo_bono.pk,
                "monto": "100000",
            },
        )
        self.assertRedirects(res, reverse("novedades:lista_novedades"))
        # No debe haberse creado
        self.assertFalse(
            Novedad.objects.filter(colaborador=self.colab_pedregal, monto=Decimal("100000")).exists()
        )

    # -------------------------------------------------------------
    # 5. API REST: AISLAMIENTO POR SUCURSAL
    # -------------------------------------------------------------
    def test_api_colaboradores_aislado_para_operador(self):
        api_client = APIClient()
        api_client.force_authenticate(user=self.user_pedregal)

        res = api_client.get(reverse("api:colaborador-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ruts = [item["rut"] for item in res.data["results"]]
        self.assertIn(self.colab_pedregal.rut, ruts)
        self.assertNotIn(self.colab_rancagua.rut, ruts)

    def test_api_periodos_aislado_para_operador(self):
        api_client = APIClient()
        api_client.force_authenticate(user=self.user_pedregal)

        res = api_client.get(reverse("api:periodo-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        periodo_ids = [item["id"] for item in res.data["results"]]
        self.assertIn(self.periodo_pedregal.id, periodo_ids)
        self.assertNotIn(self.periodo_rancagua.id, periodo_ids)


    def test_api_novedades_aislado_para_operador(self):
        api_client = APIClient()
        api_client.force_authenticate(user=self.user_pedregal)

        res = api_client.get(reverse("api:novedad-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        novedad_ids = [item["id"] for item in res.data["results"]]
        self.assertIn(self.novedad_pedregal.id, novedad_ids)
        self.assertNotIn(self.novedad_rancagua.id, novedad_ids)

    def test_api_crear_novedad_rechaza_otra_sucursal_para_operador(self):
        api_client = APIClient()
        api_client.force_authenticate(user=self.user_pedregal)

        # Intentar crear novedad para el período de Rancagua
        res = api_client.post(
            reverse("api:novedad-list"),
            {
                "periodo": self.periodo_rancagua.id,
                "colaborador": self.colab_rancagua.id,
                "tipo_novedad": self.tipo_bono.id,
                "monto": "80000.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
