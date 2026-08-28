from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

from .exportadores import construir_nombre_archivo, generar_archivo
from .forms import AnularNovedadForm, ExportacionForm, NovedadForm
from .models import (
    Colaborador,
    Exportacion,
    Novedad,
    PeriodoLiquidacion,
)


def inicio(request):
    return render(request, "novedades/inicio.html")

@never_cache
@login_required
def panel(request):
    contexto = {
        "colaboradores_activos": Colaborador.objects.filter(
            activo=True
        ).count(),
        "periodos_abiertos": PeriodoLiquidacion.objects.filter(
            estado=PeriodoLiquidacion.Estado.ABIERTO
        ).count(),
        "novedades_borrador": Novedad.objects.filter(
            estado=Novedad.Estado.BORRADOR
        ).count(),
        "novedades_validadas": Novedad.objects.filter(
            estado=Novedad.Estado.VALIDADA
        ).count(),
    }

    return render(request, "novedades/panel.html", contexto)

@never_cache
@login_required
def lista_novedades(request):
    registros = Novedad.objects.select_related(
        "periodo",
        "periodo__sucursal",
        "colaborador",
        "tipo_novedad",
        "creado_por",
        "validado_por",
    )

    busqueda = request.GET.get("q", "").strip()
    estado_seleccionado = request.GET.get("estado", "").strip()
    periodo_seleccionado = request.GET.get("periodo", "").strip()

    if busqueda:
        registros = registros.filter(
            Q(colaborador__nombres__icontains=busqueda)
            | Q(colaborador__apellidos__icontains=busqueda)
            | Q(colaborador__rut__icontains=busqueda)
            | Q(tipo_novedad__nombre__icontains=busqueda)
        )

    if estado_seleccionado in Novedad.Estado.values:
        registros = registros.filter(estado=estado_seleccionado)
    else:
        estado_seleccionado = ""

    if periodo_seleccionado.isdigit():
        registros = registros.filter(
            periodo_id=periodo_seleccionado
        )
    else:
        periodo_seleccionado = ""

    paginador = Paginator(registros, 15)
    pagina = paginador.get_page(request.GET.get("pagina"))

    periodos = (
        PeriodoLiquidacion.objects.select_related("sucursal")
        .order_by("-anio", "-mes", "sucursal__nombre")
    )

    contexto = {
        "pagina": pagina,
        "periodos": periodos,
        "estados": Novedad.Estado.choices,
        "busqueda": busqueda,
        "estado_seleccionado": estado_seleccionado,
        "periodo_seleccionado": periodo_seleccionado,
    }

    return render(
        request,
        "novedades/lista_novedades.html",
        contexto,
    )

@never_cache
@login_required
def crear_novedad(request):
    if request.method == "POST":
        formulario = NovedadForm(request.POST)

        if formulario.is_valid():
            novedad = formulario.save(commit=False)
            novedad.creado_por = request.user
            novedad.estado = Novedad.Estado.BORRADOR
            novedad.save()

            messages.success(
                request,
                "La novedad fue registrada correctamente como borrador.",
            )

            return redirect("novedades:lista_novedades")
    else:
        formulario = NovedadForm()

    contexto = {
        "formulario": formulario,
    }

    return render(
        request,
        "novedades/crear_novedad.html",
        contexto,
    )

@never_cache
@login_required
def editar_novedad(request, pk):
    novedad = get_object_or_404(
        Novedad.objects.select_related(
            "periodo",
            "periodo__sucursal",
            "colaborador",
            "tipo_novedad",
        ),
        pk=pk,
    )

    if not novedad.puede_editar:
        messages.error(
            request,
            (
                "Solo se pueden editar novedades en borrador "
                "pertenecientes a un período abierto."
            ),
        )
        return redirect("novedades:lista_novedades")

    if request.method == "POST":
        formulario = NovedadForm(
            request.POST,
            instance=novedad,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "La novedad fue actualizada correctamente.",
            )

            return redirect("novedades:lista_novedades")
    else:
        formulario = NovedadForm(instance=novedad)

    contexto = {
        "formulario": formulario,
        "novedad": novedad,
        "modo_edicion": True,
    }

    return render(
        request,
        "novedades/crear_novedad.html",
        contexto,
    )

@never_cache
@login_required
@require_POST
def validar_novedad(request, pk):
    novedad = get_object_or_404(
        Novedad.objects.select_related(
            "periodo",
            "periodo__sucursal",
        ),
        pk=pk,
    )

    try:
        novedad.validar(request.user)
    except ValidationError as error:
        messages.error(
            request,
            " ".join(error.messages),
        )
    else:
        messages.success(
            request,
            "La novedad fue validada correctamente.",
        )

    return redirect("novedades:lista_novedades")

@never_cache
@login_required
def anular_novedad(request, pk):
    novedad = get_object_or_404(
        Novedad.objects.select_related(
            "periodo",
            "periodo__sucursal",
            "colaborador",
            "tipo_novedad",
        ),
        pk=pk,
    )

    if not novedad.puede_anular:
        messages.error(
            request,
            "Esta novedad ya no puede ser anulada.",
        )
        return redirect("novedades:lista_novedades")

    if request.method == "POST":
        formulario = AnularNovedadForm(request.POST)

        if formulario.is_valid():
            try:
                novedad.anular(
                    request.user,
                    formulario.cleaned_data["motivo_anulacion"],
                )
            except ValidationError as error:
                formulario.add_error(
                    None,
                    " ".join(error.messages),
                )
            else:
                messages.success(
                    request,
                    "La novedad fue anulada correctamente.",
                )
                return redirect("novedades:lista_novedades")
    else:
        formulario = AnularNovedadForm()

    contexto = {
        "formulario": formulario,
        "novedad": novedad,
    }

    return render(
        request,
        "novedades/anular_novedad.html",
        contexto,
    )

@never_cache
@login_required
def exportar_novedades(request):
    exportaciones_recientes = (
        Exportacion.objects.select_related(
            "periodo",
            "periodo__sucursal",
            "generado_por",
        )
        .order_by("-fecha_generacion")[:10]
    )

    if request.method == "POST":
        formulario = ExportacionForm(request.POST)

        if formulario.is_valid():
            with transaction.atomic():
                periodo = (
                    PeriodoLiquidacion.objects.select_for_update()
                    .select_related("sucursal")
                    .get(
                        pk=formulario.cleaned_data["periodo"].pk
                    )
                )

                list(
                    Novedad.objects.select_for_update()
                    .filter(periodo=periodo)
                    .values_list("pk", flat=True)
                )

                tiene_borradores = Novedad.objects.filter(
                    periodo=periodo,
                    estado=Novedad.Estado.BORRADOR,
                ).exists()

                registros = (
                    Novedad.objects.filter(
                        periodo=periodo,
                        estado=Novedad.Estado.VALIDADA,
                    )
                    .select_related(
                        "periodo",
                        "periodo__sucursal",
                        "colaborador",
                        "tipo_novedad",
                        "validado_por",
                    )
                    .order_by(
                        "colaborador__apellidos",
                        "colaborador__nombres",
                        "tipo_novedad__nombre",
                        "id",
                    )
                )

                cantidad_registros = registros.count()

                if tiene_borradores:
                    formulario.add_error(
                        "periodo",
                        (
                            "No se puede exportar este período porque "
                            "todavía contiene novedades en borrador."
                        ),
                    )
                elif cantidad_registros == 0:
                    formulario.add_error(
                        "periodo",
                        (
                            "El período debe contener al menos una "
                            "novedad validada."
                        ),
                    )
                else:
                    formato = formulario.cleaned_data["formato"]

                    nombre_archivo = construir_nombre_archivo(
                        periodo,
                        formato,
                    )

                    contenido, tipo_contenido = generar_archivo(
                        formato,
                        registros,
                    )

                    Exportacion.objects.create(
                        periodo=periodo,
                        generado_por=request.user,
                        formato=formato,
                        nombre_archivo=nombre_archivo,
                        cantidad_registros=cantidad_registros,
                    )

                    if (
                        periodo.estado
                        != PeriodoLiquidacion.Estado.EXPORTADO
                    ):
                        campos_actualizados = ["estado"]
                        periodo.estado = (
                            PeriodoLiquidacion.Estado.EXPORTADO
                        )

                        if periodo.fecha_cierre is None:
                            periodo.fecha_cierre = timezone.now()
                            campos_actualizados.append("fecha_cierre")

                        periodo.save(
                            update_fields=campos_actualizados
                        )

                    respuesta = HttpResponse(
                        contenido,
                        content_type=tipo_contenido,
                    )
                    respuesta["Content-Disposition"] = (
                        f'attachment; filename="{nombre_archivo}"'
                    )
                    respuesta["X-Content-Type-Options"] = "nosniff"
                    respuesta["Cache-Control"] = "no-store, private"

                    return respuesta
    else:
        formulario = ExportacionForm()

    contexto = {
        "formulario": formulario,
        "exportaciones_recientes": exportaciones_recientes,
    }

    return render(
        request,
        "novedades/exportar_novedades.html",
        contexto,
    )