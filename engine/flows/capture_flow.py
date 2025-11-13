"""
Capture Flow - Fluxo de Captura de Leads
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Capturar informações iniciais do lead e qualificar interesse
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CaptureFlow:
    """
    Fluxo de captura de leads e primeiros contatos
    
    Etapas:
    1. Identificação inicial (nome, telefone)
    2. Qualificação de interesse
    3. Captura de dor/necessidade
    4. Direcionamento para próximo fluxo
    """
    
    def __init__(self, memory_engine, gpt_caller):
        """
        Inicializa o fluxo de captura
        
        Args:
            memory_engine: Instância do FT9Memory
            gpt_caller: Função para chamar GPT
        """
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("CaptureFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """
        Detecta se a mensagem deve acionar o fluxo de captura
        
        Args:
            interpretacao: Dict com intenção e metadados
            
        Returns:
            True se deve acionar este fluxo
        """
        intent = interpretacao.get("intencao", "")
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        # Triggers para captura
        triggers = [
            "primeira vez",
            "conhecer",
            "quero saber",
            "me interessei",
            "gostaria de",
            "preciso de ajuda",
            "vim pelo",
            "indicação",
        ]
        
        # Detecta se é primeiro contato ou interesse inicial
        if intent in ["saudacao", "ajuda", "interesse_inicial"]:
            return True
        
        if any(trigger in mensagem for trigger in triggers):
            return True
        
        # Verifica se persona não tem dados completos
        persona = interpretacao.get("persona", {})
        identificacao = persona.get("identificacao", {})
        
        if not identificacao.get("nome") or not identificacao.get("telefone"):
            return True
        
        return False
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """
        Executa o fluxo de captura
        
        Args:
            interpretacao: Dict com intenção e metadados
            usuario: Identificador do usuário
            
        Returns:
            Resposta processada
        """
        try:
            persona = interpretacao.get("persona", {})
            identificacao = persona.get("identificacao", {})
            historico = persona.get("historico_conversas", [])
            
            # Etapa 1: Saudação e identificação
            if not identificacao.get("nome"):
                return self._etapa_identificacao()
            
            # Etapa 2: Captura de interesse
            if len(historico) <= 2:
                return self._etapa_interesse(identificacao)
            
            # Etapa 3: Qualificação de dor
            return self._etapa_qualificacao(interpretacao, usuario)
            
        except Exception as e:
            logger.error(f"Erro no CaptureFlow: {str(e)}")
            return "Desculpe, ocorreu um erro. Pode repetir sua mensagem?"
    
    def _etapa_identificacao(self) -> str:
        """Etapa de identificação inicial"""
        return """Olá! 👋 Seja bem-vindo(a) à FT9 Intelligence!

Sou o AI9, seu assistente inteligente especializado em fisioterapia.

Para começarmos, qual é o seu nome?"""
    
    def _etapa_interesse(self, identificacao: Dict) -> str:
        """Etapa de captura de interesse"""
        nome = identificacao.get("nome", "")
        
        return f"""Prazer em conhecer você, {nome}! 😊

Estou aqui para ajudar você com:

🩺 **Tratamentos de Fisioterapia**
📚 **PTC 2025** - Programa de Tratamento Contínuo
📅 **Agendamentos** e orientações
💡 **Dúvidas** sobre procedimentos

O que te trouxe até aqui hoje?"""
    
    def _etapa_qualificacao(self, interpretacao: Dict, usuario: str) -> str:
        """Etapa de qualificação da dor/necessidade"""
        mensagem = interpretacao.get("mensagem_original", "")
        persona = interpretacao.get("persona", {})
        
        # Usar GPT para entender a dor e qualificar
        contexto = """Você é o AI9, assistente da FT9 Intelligence.
O paciente está descrevendo sua necessidade ou dor.

Sua missão:
1. Demonstrar empatia
2. Fazer perguntas qualificadoras
3. Identificar urgência
4. Direcionar para agendamento ou mais informações

Seja natural, empático e profissional."""
        
        resposta = self.gpt_caller(
            mensagem=mensagem,
            contexto=contexto,
            persona=persona
        )
        
        return resposta
    
    def proximo_fluxo(self, interpretacao: Dict) -> Optional[str]:
        """
        Determina qual deve ser o próximo fluxo
        
        Args:
            interpretacao: Dict com intenção e metadados
            
        Returns:
            Nome do próximo fluxo ou None
        """
        intent = interpretacao.get("intencao", "")
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        # Se mencionou PTC, vai para PTCFlow
        if "ptc" in mensagem or "programa" in mensagem or "tratamento contínuo" in mensagem:
            return "ptc_flow"
        
        # Se mencionou preço ou valor, vai para SalesFlow
        if any(palavra in mensagem for palavra in ["preço", "valor", "quanto custa", "investimento"]):
            return "sales_flow"
        
        # Se mencionou agendamento, vai para agendamento
        if "agendar" in mensagem or "marcar" in mensagem or "horário" in mensagem:
            return "agendamento"
        
        # Se demonstrou urgência, vai para UrgencyFlow
        if any(palavra in mensagem for palavra in ["urgente", "dor forte", "não aguento", "preciso rápido"]):
            return "urgency_flow"
        
        # Por padrão, continua no capture ou vai para sales
        return "sales_flow"
