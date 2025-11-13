"""
FT9 Flows - Módulo de Fluxos de Conversação
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Este módulo contém todos os fluxos específicos de conversação:
- capture_flow: Captura de leads e primeiros contatos
- sales_flow: Fluxo de vendas e conversão
- objections_flow: Tratamento de objeções
- ptc_flow: Fluxo PTC 2025 (curso e recorrência)
- family_flow: Expansão familiar
- urgency_flow: Criação de urgência
- return_flow: Retorno de pacientes inativos
- closing_flow: Fechamento e conversão final
"""

from .capture_flow import CaptureFlow
from .sales_flow import SalesFlow
from .objections_flow import ObjectionsFlow
from .ptc_flow import PTCFlow
from .family_flow import FamilyFlow
from .urgency_flow import UrgencyFlow
from .return_flow import ReturnFlow
from .closing_flow import ClosingFlow

__all__ = [
    "CaptureFlow",
    "SalesFlow",
    "ObjectionsFlow",
    "PTCFlow",
    "FamilyFlow",
    "UrgencyFlow",
    "ReturnFlow",
    "ClosingFlow",
]
