"""
Urgency Flow - Fluxo de Criação de Urgência
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Criar senso de urgência e acelerar decisão
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class UrgencyFlow:
    """Fluxo de criação de urgência"""
    
    def __init__(self, memory_engine, gpt_caller):
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("UrgencyFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """Detecta situações de urgência"""
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        triggers = ["urgente", "dor forte", "não aguento", "preciso rápido", 
                   "emergência", "hoje", "agora", "imediato"]
        
        return any(trigger in mensagem for trigger in triggers)
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """Executa fluxo de urgência"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        return f"""Entendo, {nome}! Vou te ajudar com urgência! 🚨

**ATENDIMENTO PRIORITÁRIO:**

⚡ **HOJE MESMO**
→ Temos horários de emergência
→ Avaliação em até 2 horas
→ Atendimento prioritário

🎯 **O QUE FAZER AGORA:**

1️⃣ Me passa seu telefone para contato direto
2️⃣ Descreva brevemente sua dor
3️⃣ Qual unidade é mais próxima de você?

Vou encaminhar para nossa equipe de emergência **AGORA**!

**IMPORTANTE:** Se for dor muito intensa ou suspeita de fratura, procure um pronto-socorro primeiro!

Qual sua situação exata?"""
    
    def proximo_fluxo(self, interpretacao: Dict) -> Optional[str]:
        return "closing_flow"  # Vai direto para fechamento urgente
