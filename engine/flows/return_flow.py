"""
Return Flow - Fluxo de Retorno de Pacientes Inativos
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Reativar pacientes inativos com abordagem personalizada
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ReturnFlow:
    """Fluxo de retorno de pacientes inativos"""
    
    def __init__(self, memory_engine, gpt_caller):
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("ReturnFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """Detecta se é paciente inativo retornando"""
        persona = interpretacao.get("persona", {})
        
        # Verifica se tem histórico mas está inativo
        historico = persona.get("historico_conversas", [])
        ultima_sessao = persona.get("ultima_sessao")
        
        if historico and ultima_sessao:
            # TODO: Verificar se última sessão foi há mais de 30 dias
            return True
        
        return False
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """Executa fluxo de retorno"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        return f"""Oi {nome}! Que bom te ver por aqui novamente! 😊

Faz um tempinho que você não aparece... Sentimos sua falta!

**COMO VOCÊ ESTÁ?**
→ A dor voltou?
→ Precisa de manutenção?
→ Surgiu algo novo?

**NOVIDADES FT9:**
🆕 Lançamos o PTC 2025 (tratamento ilimitado)
🤖 Agora temos suporte 24/7 com AI9
📱 App FT9 para acompanhamento

**OFERTA ESPECIAL DE RETORNO:**
→ 1ª sessão com 50% OFF
→ Reavaliação gratuita
→ Plano personalizado

Quer agendar? Tenho horários essa semana!"""
    
    def proximo_fluxo(self, interpretacao: Dict) -> Optional[str]:
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        if any(palavra in mensagem for palavra in ["sim", "quero", "vamos"]):
            return "closing_flow"
        
        if any(palavra in mensagem for palavra in ["ptc", "programa"]):
            return "ptc_flow"
        
        return None
