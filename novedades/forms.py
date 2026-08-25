from django import forms

from .models import (
    Colaborador,
    Exportacion,
    Novedad,
    PeriodoLiquidacion,
    TipoNovedad,
)


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



class AnularNovedadForm(forms.Form):
    motivo_anulacion = forms.CharField(
        label="Motivo de anulación",
        min_length=10,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "class": TEXTAREA_CLASSES,
                "rows": 4,
                "placeholder": (
                    "Explica por qué debe anularse esta novedad."
                ),
            }
        ),
        help_text=(
            "Escribe entre 10 y 500 caracteres. "
            "El motivo quedará registrado para auditoría."
        ),
    )

    def clean_motivo_anulacion(self):
        motivo = self.cleaned_data["motivo_anulacion"].strip()

        if len(motivo) < 10:
            raise forms.ValidationError(
                "El motivo debe tener al menos 10 caracteres."
            )

        return motivo

class ExportacionForm(forms.Form):
    periodo = forms.ModelChoiceField(
        label="Período de liquidación",
        queryset=PeriodoLiquidacion.objects.none(),
        empty_label="Seleccione un período",
        widget=forms.Select(
            attrs={"class": CONTROL_CLASSES}
        ),
        help_text=(
            "Solo se muestran períodos que contienen "
            "novedades validadas."
        ),
    )

    formato = forms.ChoiceField(
        label="Formato del archivo",
        choices=[
            ("", "Seleccione un formato"),
            *Exportacion.Formato.choices,
        ],
        widget=forms.Select(
            attrs={"class": CONTROL_CLASSES}
        ),
        help_text="Puedes descargar la información en Excel o CSV.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["periodo"].queryset = (
            PeriodoLiquidacion.objects.filter(
                novedades__estado=Novedad.Estado.VALIDADA
            )
            .select_related("sucursal")
            .distinct()
            .order_by("-anio", "-mes", "sucursal__nombre")
        )

    def clean_periodo(self):
        periodo = self.cleaned_data["periodo"]

        if periodo.novedades.filter(
            estado=Novedad.Estado.BORRADOR
        ).exists():
            raise forms.ValidationError(
                (
                    "No se puede exportar este período porque "
                    "todavía contiene novedades en borrador."
                )
            )

        if not periodo.novedades.filter(
            estado=Novedad.Estado.VALIDADA
        ).exists():
            raise forms.ValidationError(
                (
                    "El período debe contener al menos una "
                    "novedad validada."
                )
            )

        return periodo