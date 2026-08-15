from datetime import date
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import (
    AFP,
    Banco,
    Colaborador,
    Contrato,
    Exportacion,
    InstitucionSalud,
    Novedad,
    PeriodoLiquidacion,
    Sucursal,
    TipoNovedad,
)


class PaginaInicioTests(SimpleTestCase):
    def test_pagina_inicio_responde_correctamente(self):
        respuesta = self.client.get(reverse("novedades:inicio"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "Planilla de Novedades de Remuneraciones",
        )


class ModelosDominioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_prueba",
            password="ClaveSeguraPrueba2026",
        )

        cls.sucursal = Sucursal.objects.create(
            codigo="SUC-TEST",
            nombre="Sucursal Ficticia",
            direccion="Dirección de prueba",
        )

        cls.banco = Banco.objects.create(
            codigo="BAN-TEST",
            nombre="Banco Ficticio",
        )

        cls.afp = AFP.objects.create(
            codigo="AFP-TEST",
            nombre="AFP Ficticia",
        )

        cls.institucion_salud = InstitucionSalud.objects.create(
            codigo="SALUD-TEST",
            nombre="Institución Ficticia",
            tipo=InstitucionSalud.Tipo.FONASA,
        )

        cls.colaborador = Colaborador.objects.create(
            rut="TEST00000001",
            nombres="Nombre Ficticio",
            apellidos="Apellido de Prueba",
            sucursal=cls.sucursal,
            banco=cls.banco,
            numero_cuenta="CUENTA-FICTICIA-001",
            tipo_cuenta=Colaborador.TipoCuenta.CORRIENTE,
            afp=cls.afp,
            institucion_salud=cls.institucion_salud,
            cargas_familiares=0,
            seguro_cesantia=True,
        )

        cls.periodo = PeriodoLiquidacion.objects.create(
            sucursal=cls.sucursal,
            anio=2026,
            mes=8,
            fecha_inicio=date(2026, 8, 1),
        )

        cls.tipo_novedad = TipoNovedad.objects.create(
            codigo="BONO_PRUEBA",
            nombre="Bono ficticio",
            unidad_medida=TipoNovedad.UnidadMedida.PESOS,
            naturaleza=TipoNovedad.Naturaleza.HABER,
        )

    def test_creacion_de_catalogos_y_colaborador(self):
        self.assertEqual(Sucursal.objects.count(), 1)
        self.assertEqual(Banco.objects.count(), 1)
        self.assertEqual(AFP.objects.count(), 1)
        self.assertEqual(InstitucionSalud.objects.count(), 1)
        self.assertEqual(Colaborador.objects.count(), 1)
        self.assertEqual(self.colaborador.sucursal, self.sucursal)
        self.assertEqual(self.colaborador.banco, self.banco)
        self.assertEqual(self.colaborador.afp, self.afp)
        self.assertEqual(
            self.colaborador.institucion_salud,
            self.institucion_salud,
        )

    def test_creacion_de_contrato_valido(self):
        contrato = Contrato.objects.create(
            colaborador=self.colaborador,
            fecha_inicio=date(2026, 1, 1),
            tipo_contrato=Contrato.TipoContrato.INDEFINIDO,
            sueldo_base=Decimal("900000.00"),
            cargo="Cargo ficticio",
            centro_costo="CC-TEST",
        )

        self.assertTrue(contrato.activo)
        self.assertEqual(contrato.sueldo_base, Decimal("900000.00"))

    def test_no_permite_dos_contratos_activos(self):
        Contrato.objects.create(
            colaborador=self.colaborador,
            fecha_inicio=date(2026, 1, 1),
            tipo_contrato=Contrato.TipoContrato.INDEFINIDO,
            sueldo_base=Decimal("900000.00"),
            cargo="Cargo ficticio",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Contrato.objects.create(
                    colaborador=self.colaborador,
                    fecha_inicio=date(2026, 6, 1),
                    tipo_contrato=Contrato.TipoContrato.PLAZO_FIJO,
                    sueldo_base=Decimal("950000.00"),
                    cargo="Segundo cargo ficticio",
                )

    def test_no_permite_periodos_duplicados(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PeriodoLiquidacion.objects.create(
                    sucursal=self.sucursal,
                    anio=2026,
                    mes=8,
                    fecha_inicio=date(2026, 8, 2),
                )

    def test_no_permite_monto_negativo(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Novedad.objects.create(
                    periodo=self.periodo,
                    colaborador=self.colaborador,
                    tipo_novedad=self.tipo_novedad,
                    monto=Decimal("-100.00"),
                    creado_por=self.usuario,
                )

    def test_creacion_de_novedad_y_exportacion(self):
        novedad = Novedad.objects.create(
            periodo=self.periodo,
            colaborador=self.colaborador,
            tipo_novedad=self.tipo_novedad,
            monto=Decimal("125000.00"),
            observacion="Registro completamente ficticio.",
            creado_por=self.usuario,
        )

        exportacion = Exportacion.objects.create(
            periodo=self.periodo,
            generado_por=self.usuario,
            formato=Exportacion.Formato.XLSX,
            nombre_archivo="novedades_ficticias_2026_08.xlsx",
            cantidad_registros=1,
        )

        self.assertEqual(novedad.estado, Novedad.Estado.BORRADOR)
        self.assertEqual(novedad.monto, Decimal("125000.00"))
        self.assertEqual(exportacion.cantidad_registros, 1)
        self.assertEqual(exportacion.formato, Exportacion.Formato.XLSX)

    def test_los_diez_modelos_estan_registrados_en_admin(self):
        modelos = (
            Sucursal,
            Banco,
            AFP,
            InstitucionSalud,
            Colaborador,
            Contrato,
            PeriodoLiquidacion,
            TipoNovedad,
            Novedad,
            Exportacion,
        )

        for modelo in modelos:
            with self.subTest(modelo=modelo.__name__):
                self.assertTrue(admin.site.is_registered(modelo))