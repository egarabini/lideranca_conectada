"""
Liderança Conectada 360 Graus
==============================
Módulo principal para estratégias de liderança,
performance sustentável e continuidade do negócio.
"""

from .estrategias import EstrategiaLideranca, PerformanceSustentavel
from .continuidade import PlanoContinuidade, RiscoOrganizacional
from .indicadores import IndicadoresPerformance, PainelLideranca

__all__ = [
    "EstrategiaLideranca",
    "PerformanceSustentavel",
    "PlanoContinuidade",
    "RiscoOrganizacional",
    "IndicadoresPerformance",
    "PainelLideranca",
]

__version__ = "1.0.0"
