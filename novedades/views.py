from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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