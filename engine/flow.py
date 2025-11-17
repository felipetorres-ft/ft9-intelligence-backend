"""
FT9 Flow Manager - Gerenciador de Fluxos de Conversação
Versão 2.0 - Integrado com 8 Fluxos Modulares
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025
"""
import logging
import os
from typing import Dict, Any, Optional
import requests

# Importar fluxos modulares
from .flows import (
    CaptureFlow,
    SalesFlow,
    ObjectionsFlow,
    PTCFlow,
    FamilyFlow,
    UrgencyFlow,
    ReturnFlow,
    ClosingFlow
)

logger = logging.getLogger(__name__)


class FT9Flow:
    """
    Gerenciador de fluxos de conversação do FT9 Intelligence
    Versão 2.0 - Integrado com 8 fluxos modulares especializados
    """
    
    def __init__(self, memory_engine):
        """
        Inicializa o gerenciador de fluxos
        
        Args:
            memory_engine: Instância do FT9Memory
        """
        self.memory = memory_engine
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Inicializar fluxos modulares
        self.capture_flow = CaptureFlow(memory_engine, self._chamar_gpt)
        self.sales_flow = SalesFlow(memory_engine, self._chamar_gpt)
        self.objections_flow = ObjectionsFlow(memory_engine, self._chamar_gpt)
        self.ptc_flow = PTCFlow(memory_engine, self._chamar_gpt)
        self.family_flow = FamilyFlow(memory_engine, self._chamar_gpt)
        self.urgency_flow = UrgencyFlow(memory_engine, self._chamar_gpt)
        self.return_flow = ReturnFlow(memory_engine, self._chamar_gpt)
        self.closing_flow = ClosingFlow(memory_engine, self._chamar_gpt)
        
        logger.info("FT9Flow v2.0 inicializado com 8 fluxos modulares")
    
    def executar_fluxo(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """
        Executa o fluxo apropriado baseado na interpretação
        
        Ordem de prioridade:
        1. UrgencyFlow (máxima prioridade)
        2. ClosingFlow (conversão)
        3. ObjectionsFlow (tratamento de objeções)
        4. PTCFlow (programa específico)
        5. FamilyFlow (expansão)
        6. ReturnFlow (reativação)
        7. SalesFlow (vendas)
        8. CaptureFlow (captura inicial)
        
        Args:
            interpretacao: Dict com intenção e metadados
            usuario: Identificador do usuário
            
        Returns:
            Resposta processada
        """
        try:
            # 1. URGÊNCIA - Máxima prioridade
            if self.urgency_flow.detectar(interpretacao):
                logger.info(f"Acionando UrgencyFlow para {usuario}")
                return self.urgency_flow.executar(interpretacao, usuario)
            
            # 2. FECHAMENTO - Alta prioridade (conversão)
            if self.closing_flow.detectar(interpretacao):
                logger.info(f"Acionando ClosingFlow para {usuario}")
                return self.closing_flow.executar(interpretacao, usuario)
            
            # 3. OBJEÇÕES - Tratar antes de continuar vendas
            if self.objections_flow.detectar(interpretacao):
                logger.info(f"Acionando ObjectionsFlow para {usuario}")
                resposta = self.objections_flow.executar(interpretacao, usuario)
                
                # Verificar próximo fluxo
                proximo = self.objections_flow.proximo_fluxo(interpretacao)
                if proximo:
                    logger.info(f"Próximo fluxo sugerido: {proximo}")
                
                return resposta
            
            # 4. PTC - Programa específico
            if self.ptc_flow.detectar(interpretacao):
                logger.info(f"Acionando PTCFlow para {usuario}")
                resposta = self.ptc_flow.executar(interpretacao, usuario)
                
                # Verificar próximo fluxo
                proximo = self.ptc_flow.proximo_fluxo(interpretacao)
                if proximo:
                    logger.info(f"Próximo fluxo sugerido: {proximo}")
                
                return resposta
            
            # 5. FAMÍLIA - Expansão familiar
            if self.family_flow.detectar(interpretacao):
                logger.info(f"Acionando FamilyFlow para {usuario}")
                return self.family_flow.executar(interpretacao, usuario)
            
            # 6. RETORNO - Reativação de inativos
            if self.return_flow.detectar(interpretacao):
                logger.info(f"Acionando ReturnFlow para {usuario}")
                return self.return_flow.executar(interpretacao, usuario)
            
            # 7. VENDAS - Processo comercial
            if self.sales_flow.detectar(interpretacao):
                logger.info(f"Acionando SalesFlow para {usuario}")
                resposta = self.sales_flow.executar(interpretacao, usuario)
                
                # Verificar próximo fluxo
                proximo = self.sales_flow.proximo_fluxo(interpretacao)
                if proximo:
                    logger.info(f"Próximo fluxo sugerido: {proximo}")
                
                return resposta
            
            # 8. CAPTURA - Primeiro contato e qualificação
            if self.capture_flow.detectar(interpretacao):
                logger.info(f"Acionando CaptureFlow para {usuario}")
                resposta = self.capture_flow.executar(interpretacao, usuario)
                
                # Verificar próximo fluxo
                proximo = self.capture_flow.proximo_fluxo(interpretacao)
                if proximo:
                    logger.info(f"Próximo fluxo sugerido: {proximo}")
                
                return resposta
            
            # FALLBACK - Fluxos legados para compatibilidade
            intent = interpretacao.get("intencao", "")
            
            if intent == "agendamento":
                return self._fluxo_agendamento(interpretacao, usuario)
            elif intent == "ajuda":
                return self._fluxo_ajuda(interpretacao, usuario)
            elif intent == "saudacao":
                return self._fluxo_saudacao(interpretacao, usuario)
            else:
                return self._fluxo_mensagem_livre(interpretacao, usuario)
                
        except Exception as e:
            logger.error(f"Erro ao executar fluxo: {str(e)}")
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."
    
    # ========== FLUXOS LEGADOS (COMPATIBILIDADE) ==========
    
    def _fluxo_agendamento(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de agendamento (legado)"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        saudacao = f"Olá {nome}! " if nome else "Olá! "
        
        return f"""{saudacao}Vou te ajudar com o agendamento! 📅

Para agendar sua sessão, preciso de algumas informações:

1️⃣ **Qual unidade você prefere?**
   → FT9 Moema
   → FT9 Pinheiros
   → FT9 Itaim

2️⃣ **Qual melhor dia/horário?**
   → Manhã (8h-12h)
   → Tarde (13h-18h)
   → Noite (18h-21h)

Me conta suas preferências!"""
    
    def _fluxo_saudacao(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de saudação (legado)"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        if nome:
            return f"Olá {nome}! 👋 Como posso ajudar você hoje?"
        else:
            return "Olá! 👋 Sou o AI9, assistente inteligente da FT9. Como posso ajudar você hoje?"
    
    def _fluxo_ajuda(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de ajuda (legado)"""
        return """🤖 **AI9 - Assistente FT9 Intelligence**

Posso ajudar você com:

🩺 **Tratamentos** - Informações sobre fisioterapia
📦 **Planos** - PTC 2025 e pacotes
💰 **Preços** - Valores e formas de pagamento
📅 **Agendamentos** - Marcar sua sessão
❓ **Dúvidas** - Qualquer pergunta

Como posso ajudar você hoje?"""
    
    def _fluxo_mensagem_livre(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de mensagem livre (legado)"""
        mensagem = interpretacao.get("mensagem_original", "")
        persona = interpretacao.get("persona", {})
        
        # Chamar GPT para resposta natural
        contexto = """Você é o AI9, assistente da FT9 Intelligence.

Responda de forma natural, empática e profissional.
Se a mensagem indicar interesse comercial, conduza para vendas.
Se houver dúvidas, esclareça e ofereça ajuda."""
        
        resposta = self._chamar_gpt(
            mensagem=mensagem,
            contexto=contexto,
            persona=persona
        )
        
        return resposta
    
    # ========== FUNÇÕES AUXILIARES ==========
    
    def _chamar_gpt(
        self, 
        mensagem: str, 
        contexto: str, 
        persona: Optional[Dict] = None
    ) -> str:
        """
        Chama GPT para gerar resposta
        
        Args:
            mensagem: Mensagem do usuário
            contexto: Contexto da conversa
            persona: Dados da persona do usuário
            
        Returns:
            Resposta gerada pelo GPT
        """
        try:
            # Construir prompt com contexto e persona
            system_prompt = self._construir_system_prompt(persona, contexto)
            
            # Chamar API OpenAI
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4.1-mini",  # Usar modelo disponível no Manus
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensagem}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                resposta = result["choices"][0]["message"]["content"]
                logger.info("Resposta GPT gerada com sucesso")
                return resposta
            else:
                logger.error(f"Erro na API OpenAI: {response.status_code}")
                return "Desculpe, não consegui processar sua mensagem no momento."
                
        except Exception as e:
            logger.error(f"Erro ao chamar GPT: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."
    
    def _construir_system_prompt(
        self, 
        persona: Optional[Dict] = None,
        contexto_adicional: str = ""
    ) -> str:
        """
        Constrói o system prompt para GPT
        
        Args:
            persona: Dados da persona do usuário
            contexto_adicional: Contexto adicional do fluxo
            
        Returns:
            System prompt personalizado
        """
        # Prompt base AI9
        prompt = """Você é o AI9, assistente inteligente da FT9 Intelligence.

Você foi desenvolvido por Felipe Torres (Felipe Teixeira) com base na metodologia dos 9 Pilares do Empreendedorismo, especializada em empreendedorismo para área de saúde.

Características:
- Profissional mas acessível
- Empático e consultivo
- Objetivo e direto
- Baseado em dados reais
- Transparente sobre limitações
- Focado em resultados

IMPORTANTE:
- Seja natural e conversacional
- Use emojis com moderação
- Conduza para ação (agendamento, fechamento)
- Sempre ofereça próximo passo claro"""
        
        # Adicionar contexto adicional do fluxo
        if contexto_adicional:
            prompt += f"\n\n{contexto_adicional}"
        
        # Adicionar informações da persona se disponível
        if persona:
            identificacao = persona.get("identificacao", {})
            nome = identificacao.get("nome", "")
            
            if nome:
                prompt += f"\n\nVocê está conversando com {nome}."
            
            # Adicionar contexto de relacionamento
            relacao = persona.get("relacao_com_FT", {})
            if relacao:
                prompt += f"\nContexto: {relacao}"
        
        return prompt
