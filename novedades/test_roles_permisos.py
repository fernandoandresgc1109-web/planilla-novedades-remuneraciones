from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
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
from .permisos import (
    NOMBRE_GRUPO_CONTABILIDAD,
    configurar_grupos_permisos,
    es_usuario_contabilidad,
    puede_modificar_novedades,
)


class RolesYPermisosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        configurar_grupos_permisos()
        cls.grupo_contabilidad = Group.objects.get(
            name=NOMBRE_GRUPO_CONTABILIDAD
        )

        User = get_user_model()
        cls.clave = "ClaveSegura2026!"

        # Usuario con perfil Contabilidad
        cls.usuario_contabilidad = User.objects.create_user(
            username="contador_test",
            password=cls.clave,
            first_name="Carlos",
            last_name="Contabilidad",
        )
        cls.usuario_contabilidad.groups.add(cls.grupo_contabilidad)

        # Usuario operador estándar
        cls.usuario_operador = User.objects.create_user(
            username="operador_test",
            password=cls.clave,
            first_name="Olga",
            last_name="Operaciones",
        )

        # Entidades base para pruebas
        cls.sucursal = Sucursal.objects.create(
            codigo="SUC-TEST",
            nombre="Sucursal Central",
            activo=True,
        )
        cls.banco = Banco.objects.create(
            codigo="BCO-TEST",
            nombre="Banco Test",
            activo=True,
        )
        cls.afp = AFP.objects.create(
            codigo="AFP-TEST",
            nombre="AFP Test",
            activo=True,
        )
        cls.salud = InstitucionSalud.objects.create(
            codigo="FON-TEST",
            nombre="FONASA",
            tipo=InstitucionSalud.Tipo.FONASA,
            activo=True,
        )
        cls.colaborador = Colaborador.objects.create(
            rut="11.111.111-1",
            nombres="Juan",
            apellidos="Pérez",
            sucursal=cls.sucursal,
            banco=cls.banco,
            afp=cls.afp,
            institucion_salud=cls.salud,
            cargas_familiares=0,
            seguro_cesantia=True,
            activo=True,
        )
        cls.periodo = PeriodoLiquidacion.objects.create(
            sucursal=cls.sucursal,
            anio=2026,
            mes=9,
            fecha_inicio=date(2026, 9, 1),
            estado=PeriodoLiquidacion.Estado.ABIERTO,
        )
        cls.tipo_novedad = TipoNovedad.objects.create(
            codigo="BONO-TEST",
            nombre="Bono Desempeño",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
            activo=True,
        )

    def test_comando_crear_roles(self):
        call_command("crear_roles")
        self.assertTrue(
            Group.objects.filter(name=NOMBRE_GRUPO_CONTABILIDAD).exists()
        )

    def test_verificacion_funciones_permiso(self):
        self.assertTrue(es_usuario_contabilidad(self.usuario_contabilidad))
        self.assertFalse(es_usuario_contabilidad(self.usuario_operador))

        self.assertFalse(puede_modificar_novedades(self.usuario_contabilidad))
        self.assertTrue(puede_modificar_novedades(self.usuario_operador))

    def test_usuario_contabilidad_accede_panel(self):
        self.client.force_login(self.usuario_contabilidad)
        respuesta = self.client.get(reverse("novedades:panel"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "Contabilidad (Solo lectura y exportación)",
        )

    def test_usuario_contabilidad_ve_lista_sin_botones_mutacion(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            creado_por=self.usuario_operador,
        )

        self.client.force_login(self.usuario_contabilidad)
        respuesta = self.client.get(reverse("novedades:lista_novedades"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Modo solo lectura y exportación")
        self.assertContains(respuesta, "Solo lectura")
        self.assertNotContains(respuesta, "+ Registrar novedad")
        self.assertNotContains(
            respuesta,
            reverse("novedades:editar_novedad", args=[novedad.pk]),
        )
        self.assertNotContains(
            respuesta,
            reverse("novedades:validar_novedad", args=[novedad.pk]),
        )
        self.assertNotContains(
            respuesta,
            reverse("novedades:anular_novedad", args=[novedad.pk]),
        )

    def test_usuario_contabilidad_bloqueado_crear_novedad_web(self):
        self.client.force_login(self.usuario_contabilidad)

        respuesta_get = self.client.get(reverse("novedades:crear_novedad"))
        self.assertRedirects(respuesta_get, reverse("novedades:lista_novedades"))

        conteo_inicial = Novedad.objects.count()
        respuesta_post = self.client.post(
            reverse("novedades:crear_novedad"),
            {
                "periodo": self.periodo.pk,
                "colaborador": self.colaborador.pk,
                "tipo_novedad": self.tipo_novedad.pk,
                "monto": 25000,
            },
        )
        self.assertRedirects(respuesta_post, reverse("novedades:lista_novedades"))
        self.assertEqual(Novedad.objects.count(), conteo_inicial)

    def test_usuario_contabilidad_bloqueado_editar_novedad_web(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            creado_por=self.usuario_operador,
        )

        self.client.force_login(self.usuario_contabilidad)

        respuesta_get = self.client.get(
            reverse("novedades:editar_novedad", args=[novedad.pk])
        )
        self.assertRedirects(respuesta_get, reverse("novedades:lista_novedades"))

        respuesta_post = self.client.post(
            reverse("novedades:editar_novedad", args=[novedad.pk]),
            {
                "periodo": self.periodo.pk,
                "colaborador": self.colaborador.pk,
                "tipo_novedad": self.tipo_novedad.pk,
                "monto": 99999,
            },
        )
        self.assertRedirects(respuesta_post, reverse("novedades:lista_novedades"))
        novedad.refresh_from_db()
        self.assertEqual(novedad.monto, 50000)

    def test_usuario_contabilidad_bloqueado_validar_novedad_web(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            creado_por=self.usuario_operador,
        )

        self.client.force_login(self.usuario_contabilidad)
        respuesta = self.client.post(
            reverse("novedades:validar_novedad", args=[novedad.pk])
        )
        self.assertRedirects(respuesta, reverse("novedades:lista_novedades"))

        novedad.refresh_from_db()
        self.assertEqual(novedad.estado, Novedad.Estado.BORRADOR)

    def test_usuario_contabilidad_bloqueado_anular_novedad_web(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            creado_por=self.usuario_operador,
        )

        self.client.force_login(self.usuario_contabilidad)

        respuesta_get = self.client.get(
            reverse("novedades:anular_novedad", args=[novedad.pk])
        )
        self.assertRedirects(respuesta_get, reverse("novedades:lista_novedades"))

        respuesta_post = self.client.post(
            reverse("novedades:anular_novedad", args=[novedad.pk]),
            {"motivo_anulacion": "Motivo de prueba con longitud suficiente"},
        )
        self.assertRedirects(respuesta_post, reverse("novedades:lista_novedades"))

        novedad.refresh_from_db()
        self.assertEqual(novedad.estado, Novedad.Estado.BORRADOR)

    def test_usuario_contabilidad_puede_exportar_excel(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            creado_por=self.usuario_operador,
        )
        novedad.validar(self.usuario_operador)

        self.client.force_login(self.usuario_contabilidad)

        # GET exportaciones
        respuesta_get = self.client.get(reverse("novedades:exportar_novedades"))
        self.assertEqual(respuesta_get.status_code, 200)

        # POST exportación XLSX
        respuesta_post = self.client.post(
            reverse("novedades:exportar_novedades"),
            {
                "periodo": self.periodo.pk,
                "formato": "XLSX",
            },
        )
        self.assertEqual(respuesta_post.status_code, 200)
        self.assertEqual(
            respuesta_post.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(".xlsx", respuesta_post.headers["Content-Disposition"])

    def test_usuario_contabilidad_api_solo_lectura(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=50000,
            creado_por=self.usuario_operador,
        )

        api_client = APIClient()
        api_client.force_login(self.usuario_contabilidad)

        # GET está permitido
        respuesta_get = api_client.get(reverse("api:novedad-list"))
        self.assertEqual(respuesta_get.status_code, 200)

        # POST creación novedad está bloqueado con 403
        respuesta_post = api_client.post(
            reverse("api:novedad-list"),
            {
                "periodo": self.periodo.pk,
                "colaborador": self.colaborador.pk,
                "tipo_novedad": self.tipo_novedad.pk,
                "monto": 30000,
            },
            format="json",
        )
        self.assertEqual(respuesta_post.status_code, 403)

        # PATCH edición novedad está bloqueado con 403
        respuesta_patch = api_client.patch(
            reverse("api:novedad-detail", args=[novedad.pk]),
            {"monto": 40000},
            format="json",
        )
        self.assertEqual(respuesta_patch.status_code, 403)

        # POST validar novedad está bloqueado con 403
        respuesta_validar = api_client.post(
            reverse("api:novedad-validar", args=[novedad.pk]),
            format="json",
        )
        self.assertEqual(respuesta_validar.status_code, 403)

        # POST anular novedad está bloqueado con 403
        respuesta_anular = api_client.post(
            reverse("api:novedad-anular", args=[novedad.pk]),
            {"motivo_anulacion": "Motivo de prueba con longitud suficiente"},
            format="json",
        )
        self.assertEqual(respuesta_anular.status_code, 403)

        # POST colaborador está bloqueado con 403
        respuesta_colab = api_client.post(
            reverse("api:colaborador-list"),
            {
                "rut": "22.222.222-2",
                "nombres": "Pedro",
                "apellidos": "Gómez",
                "sucursal": self.sucursal.pk,
                "afp": self.afp.pk,
                "institucion_salud": self.salud.pk,
            },
            format="json",
        )
        self.assertEqual(respuesta_colab.status_code, 403)

    def test_usuario_operador_puede_crear_y_gestionar_novedades(self):
        self.client.force_login(self.usuario_operador)

        # Puede acceder a crear
        respuesta_get = self.client.get(reverse("novedades:crear_novedad"))
        self.assertEqual(respuesta_get.status_code, 200)

        # Puede crear
        respuesta_post = self.client.post(
            reverse("novedades:crear_novedad"),
            {
                "periodo": self.periodo.pk,
                "colaborador": self.colaborador.pk,
                "tipo_novedad": self.tipo_novedad.pk,
                "monto": 35000,
            },
        )
        self.assertRedirects(respuesta_post, reverse("novedades:lista_novedades"))

        novedad = Novedad.objects.filter(monto=35000).first()
        self.assertIsNotNone(novedad)

        # Puede validar
        respuesta_val = self.client.post(
            reverse("novedades:validar_novedad", args=[novedad.pk])
        )
        self.assertRedirects(respuesta_val, reverse("novedades:lista_novedades"))
        novedad.refresh_from_db()
        self.assertEqual(novedad.estado, Novedad.Estado.VALIDADA)

    def test_usuario_nombre_contabilidad_sin_grupo_explicito_es_restringido(self):
        User = get_user_model()
        usuario_solo_nombre = User.objects.create_user(
            username="Contabilidad",
            password=self.clave,
        )

        self.assertTrue(es_usuario_contabilidad(usuario_solo_nombre))
        self.assertFalse(puede_modificar_novedades(usuario_solo_nombre))

        self.client.force_login(usuario_solo_nombre)
        respuesta = self.client.get(reverse("novedades:crear_novedad"))
        self.assertRedirects(respuesta, reverse("novedades:lista_novedades"))

    def test_usuario_nombre_contabilidad_como_superusuario_sigue_restringido(self):
        User = get_user_model()
        super_contabilidad = User.objects.create_superuser(
            username="contabilidad_admin",
            password=self.clave,
        )

        self.assertTrue(es_usuario_contabilidad(super_contabilidad))
        self.assertFalse(puede_modificar_novedades(super_contabilidad))

        self.client.force_login(super_contabilidad)
        respuesta = self.client.get(reverse("novedades:crear_novedad"))
        self.assertRedirects(respuesta, reverse("novedades:lista_novedades"))

    def test_usuario_contabilidad_no_puede_agregar_en_django_admin(self):
        User = get_user_model()
        staff_contabilidad = User.objects.create_user(
            username="contabilidad_staff",
            password=self.clave,
            is_staff=True,
        )
        self.client.force_login(staff_contabilidad)

        # GET agregar novedad en admin
        respuesta = self.client.get(reverse("admin:novedades_novedad_add"))
        self.assertEqual(respuesta.status_code, 403)
