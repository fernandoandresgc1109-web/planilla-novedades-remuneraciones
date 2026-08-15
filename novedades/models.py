from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Sucursal(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "sucursal"
        verbose_name_plural = "sucursales"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Banco(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "banco"
        verbose_name_plural = "bancos"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class AFP(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "AFP"
        verbose_name_plural = "AFP"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class InstitucionSalud(models.Model):
    class Tipo(models.TextChoices):
        FONASA = "FONASA", "FONASA"
        ISAPRE = "ISAPRE", "ISAPRE"

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "institución de salud"
        verbose_name_plural = "instituciones de salud"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Colaborador(models.Model):
    class TipoCuenta(models.TextChoices):
        CORRIENTE = "CORRIENTE", "Cuenta corriente"
        VISTA = "VISTA", "Cuenta vista"
        AHORRO = "AHORRO", "Cuenta de ahorro"
        CUENTA_RUT = "CUENTA_RUT", "Cuenta RUT"
        OTRA = "OTRA", "Otra"

    rut = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="colaboradores",
    )
    banco = models.ForeignKey(
        Banco,
        on_delete=models.PROTECT,
        related_name="colaboradores",
        null=True,
        blank=True,
    )
    numero_cuenta = models.CharField(max_length=30, blank=True)
    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TipoCuenta.choices,
        blank=True,
    )
    afp = models.ForeignKey(
        AFP,
        on_delete=models.PROTECT,
        related_name="colaboradores",
    )
    institucion_salud = models.ForeignKey(
        InstitucionSalud,
        on_delete=models.PROTECT,
        related_name="colaboradores",
    )
    cargas_familiares = models.PositiveSmallIntegerField(default=0)
    seguro_cesantia = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "colaborador"
        verbose_name_plural = "colaboradores"

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"


class Contrato(models.Model):
    class TipoContrato(models.TextChoices):
        INDEFINIDO = "INDEFINIDO", "Indefinido"
        PLAZO_FIJO = "PLAZO_FIJO", "Plazo fijo"
        OTRO = "OTRO", "Otro"

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT,
        related_name="contratos",
    )
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField(null=True, blank=True)
    tipo_contrato = models.CharField(
        max_length=20,
        choices=TipoContrato.choices,
    )
    sueldo_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    cargo = models.CharField(max_length=100)
    centro_costo = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha_inicio"]
        verbose_name = "contrato"
        verbose_name_plural = "contratos"
        constraints = [
            models.UniqueConstraint(
                fields=["colaborador"],
                condition=models.Q(activo=True),
                name="unico_contrato_activo_colaborador",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(fecha_termino__isnull=True)
                    | models.Q(fecha_termino__gte=models.F("fecha_inicio"))
                ),
                name="contrato_fecha_termino_valida",
            ),
            models.CheckConstraint(
                condition=models.Q(sueldo_base__gt=0),
                name="contrato_sueldo_base_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.colaborador} - {self.get_tipo_contrato_display()}"

class PeriodoLiquidacion(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = "ABIERTO", "Abierto"
        CERRADO = "CERRADO", "Cerrado"
        EXPORTADO = "EXPORTADO", "Exportado"

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="periodos_liquidacion",
    )
    anio = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2100),
        ],
    )
    mes = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
    )
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.ABIERTO,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-anio", "-mes"]
        verbose_name = "período de liquidación"
        verbose_name_plural = "períodos de liquidación"
        constraints = [
            models.UniqueConstraint(
                fields=["sucursal", "anio", "mes"],
                name="periodo_unico_sucursal_anio_mes",
            ),
            models.CheckConstraint(
                condition=models.Q(anio__gte=2000, anio__lte=2100),
                name="periodo_anio_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(mes__gte=1, mes__lte=12),
                name="periodo_mes_valido",
            ),
        ]

    def __str__(self):
        return f"{self.sucursal} - {self.mes:02d}/{self.anio}"


class TipoNovedad(models.Model):
    class UnidadMedida(models.TextChoices):
        DIAS = "DIAS", "Días"
        MINUTOS = "MINUTOS", "Minutos"
        PESOS = "PESOS", "Pesos"
        REGISTRO = "REGISTRO", "Registro"

    class Naturaleza(models.TextChoices):
        ASISTENCIA = "ASISTENCIA", "Asistencia"
        HABER = "HABER", "Haber"
        DESCUENTO = "DESCUENTO", "Descuento"
        INFORMATIVO = "INFORMATIVO", "Informativo"

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    unidad_medida = models.CharField(
        max_length=15,
        choices=UnidadMedida.choices,
    )
    naturaleza = models.CharField(
        max_length=15,
        choices=Naturaleza.choices,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "tipo de novedad"
        verbose_name_plural = "tipos de novedad"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Novedad(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        VALIDADA = "VALIDADA", "Validada"
        ANULADA = "ANULADA", "Anulada"

    periodo = models.ForeignKey(
        PeriodoLiquidacion,
        on_delete=models.PROTECT,
        related_name="novedades",
    )
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT,
        related_name="novedades",
    )
    tipo_novedad = models.ForeignKey(
        TipoNovedad,
        on_delete=models.PROTECT,
        related_name="novedades",
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_termino = models.DateField(null=True, blank=True)
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )
    observacion = models.TextField(blank=True)
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="novedades_creadas",
    )
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="novedades_validadas",
        null=True,
        blank=True,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "novedad"
        verbose_name_plural = "novedades"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(fecha_inicio__isnull=True)
                    | models.Q(fecha_termino__isnull=True)
                    | models.Q(fecha_termino__gte=models.F("fecha_inicio"))
                ),
                name="novedad_fechas_validas",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(cantidad__isnull=True)
                    | models.Q(cantidad__gte=0)
                ),
                name="novedad_cantidad_no_negativa",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(monto__isnull=True)
                    | models.Q(monto__gte=0)
                ),
                name="novedad_monto_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.tipo_novedad} - {self.colaborador} ({self.periodo})"


class Exportacion(models.Model):
    class Formato(models.TextChoices):
        XLSX = "XLSX", "Excel"
        CSV = "CSV", "CSV"

    periodo = models.ForeignKey(
        PeriodoLiquidacion,
        on_delete=models.PROTECT,
        related_name="exportaciones",
    )
    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="exportaciones_generadas",
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    formato = models.CharField(
        max_length=10,
        choices=Formato.choices,
    )
    nombre_archivo = models.CharField(max_length=255)
    cantidad_registros = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-fecha_generacion"]
        verbose_name = "exportación"
        verbose_name_plural = "exportaciones"

    def __str__(self):
        return self.nombre_archivo