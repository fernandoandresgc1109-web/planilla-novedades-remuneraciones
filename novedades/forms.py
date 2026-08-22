from django import forms

from .models import Colaborador, Novedad, PeriodoLiquidacion, TipoNovedad


CONTROL_CLASSES = (
    "mt-2 block w-full rounded-xl border border-slate-300 bg-white "
    "px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition "
    "focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
)

TEXTAREA_CLASSES = (
    "mt-2 block min-h-28 w-full resize-y rounded-xl border "
    "border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 "
    "shadow-sm outline-none transition focus:border-emerald-500 "
    "focus:ring-4 focus:ring-emerald-100"
)


class NovedadForm(forms.ModelForm):
    class Meta:
        model = Novedad
        fields = [
            "periodo",
            "colaborador",
            "tipo_novedad",
            "fecha_inicio",
            "fecha_termino",
            "cantidad",
            "monto",
            "observacion",
        ]
        labels = {
            "periodo": "Período de liquidación",
            "colaborador": "Colaborador",
            "tipo_novedad": "Tipo de novedad",
            "fecha_inicio": "Fecha de inicio",
            "fecha_termino": "Fecha de término",
            "cantidad": "Cantidad",
            "monto": "Monto",
            "observacion": "Observación",
        }
        widgets = {
            "periodo": forms.Select(
                attrs={"class": CONTROL_CLASSES}
            ),
            "colaborador": forms.Select(
                attrs={"class": CONTROL_CLASSES}
            ),
            "tipo_novedad": forms.Select(
                attrs={"class": CONTROL_CLASSES}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": CONTROL_CLASSES,
                    "type": "date",
                }
            ),
            "fecha_termino": forms.DateInput(
                attrs={
                    "class": CONTROL_CLASSES,
                    "type": "date",
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": CONTROL_CLASSES,
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Ejemplo: 2.00",
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": CONTROL_CLASSES,
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Ejemplo: 50000",
                }
            ),
            "observacion": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASSES,
                    "rows": 4,
                    "placeholder": (
                        "Agrega información que ayude a revisar "
                        "esta novedad."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["periodo"].queryset = (
            PeriodoLiquidacion.objects.filter(
                estado=PeriodoLiquidacion.Estado.ABIERTO
            )
            .select_related("sucursal")
            .order_by("-anio", "-mes", "sucursal__nombre")
        )

        self.fields["colaborador"].queryset = (
            Colaborador.objects.filter(activo=True)
            .select_related("sucursal")
            .order_by("apellidos", "nombres")
        )

        self.fields["tipo_novedad"].queryset = (
            TipoNovedad.objects.filter(activo=True)
            .order_by("nombre")
        )

        self.fields["periodo"].empty_label = (
            "Seleccione un período abierto"
        )
        self.fields["colaborador"].empty_label = (
            "Seleccione un colaborador"
        )
        self.fields["tipo_novedad"].empty_label = (
            "Seleccione un tipo de novedad"
        )

    def clean(self):
        datos = super().clean()

        periodo = datos.get("periodo")
        colaborador = datos.get("colaborador")
        tipo_novedad = datos.get("tipo_novedad")
        fecha_inicio = datos.get("fecha_inicio")
        fecha_termino = datos.get("fecha_termino")
        cantidad = datos.get("cantidad")
        monto = datos.get("monto")

        if (
            periodo
            and periodo.estado
            != PeriodoLiquidacion.Estado.ABIERTO
        ):
            self.add_error(
                "periodo",
                "Solo se pueden registrar novedades en períodos abiertos.",
            )

        if (
            periodo
            and colaborador
            and periodo.sucursal_id != colaborador.sucursal_id
        ):
            self.add_error(
                "colaborador",
                (
                    "El colaborador debe pertenecer a la misma "
                    "sucursal del período seleccionado."
                ),
            )

        if (
            fecha_inicio
            and fecha_termino
            and fecha_termino < fecha_inicio
        ):
            self.add_error(
                "fecha_termino",
                (
                    "La fecha de término no puede ser anterior "
                    "a la fecha de inicio."
                ),
            )

        if tipo_novedad:
            if (
                tipo_novedad.unidad_medida
                == TipoNovedad.UnidadMedida.PESOS
                and monto is None
            ):
                self.add_error(
                    "monto",
                    "Este tipo de novedad requiere un monto.",
                )

            if (
                tipo_novedad.unidad_medida
                in {
                    TipoNovedad.UnidadMedida.DIAS,
                    TipoNovedad.UnidadMedida.MINUTOS,
                }
                and cantidad is None
            ):
                self.add_error(
                    "cantidad",
                    "Este tipo de novedad requiere una cantidad.",
                )

        return datos