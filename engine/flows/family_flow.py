"""
Family Flow - Fluxo de Expansão Familiar
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Expandir base de pacientes através de indicações familiares
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FamilyFlow:
    """Fluxo de expansão familiar"""
    
    def __init__(self, memory_engine, gpt_caller):
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("FamilyFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """Detecta menção a familiares"""
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        triggers = ["família", "esposa", "marido", "filho", "filha", "pai", "mãe", 
                   "irmão", "irmã", "sogro", "sogra", "parente"]
        
        return any(trigger in mensagem for trigger in triggers)
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """Executa fluxo de expansão familiar"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        return f"""Que legal, {nome}! 👨‍👩‍👧‍👦

Cuidar da saúde em família é maravilhoso! Temos um **programa especial** para isso:

**PLANO FAMÍLIA PTC 2025:**

💰 **DESCONTOS PROGRESSIVOS**
→ 2 pessoas: 10% OFF (R$ 1.794/mês)
→ 3 pessoas: 15% OFF (R$ 2.542/mês)
→ 4+ pessoas: 20% OFF (R$ 3.188/mês)

✅ **BENEFÍCIOS**
→ Avaliação gratuita para todos
→ Horários sincronizados
→ Acompanhamento integrado
→ Prevenção desde cedo

👶 **TODAS AS IDADES**
→ Crianças (a partir de 5 anos)
→ Adultos
→ Idosos
→ Gestantes

Quantas pessoas da sua família têm interesse? Posso agendar avaliações gratuitas!"""
    
    def proximo_fluxo(self, interpretacao: Dict) -> Optional[str]:
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        if any(palavra in mensagem for palavra in ["quero", "vamos", "sim"]):
            return "closing_flow"
        
        return None
