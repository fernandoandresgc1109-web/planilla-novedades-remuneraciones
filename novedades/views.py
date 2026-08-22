from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import NovedadForm
from .models import Colaborador, Novedad, PeriodoLiquidacion


def inicio(request):
    return render(request, "novedades/inicio.html")


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