"""
FT9 Flow Manager - Gerenciador de Fluxos de Conversação
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025
"""
import logging
import os
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class FT9Flow:
    """
    Gerenciador de fluxos de conversação do FT9 Intelligence
    Integrado com GPT-5 e Knowledge Base PTC 2025
    """
    
    def __init__(self, memory_engine):
        """
        Inicializa o gerenciador de fluxos
        
        Args:
            memory_engine: Instância do FT9Memory
        """
        self.memory = memory_engine
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        logger.info("FT9Flow inicializado com sucesso")
    
    def executar_fluxo(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """
        Executa o fluxo apropriado baseado na interpretação
        
        Args:
            interpretacao: Dict com intenção e metadados
            usuario: Identificador do usuário
            
        Returns:
            Resposta processada
        """
        intent = interpretacao["intencao"]
        
        try:
            # Roteamento de fluxos
            if intent == "agendamento":
                return self._fluxo_agendamento(interpretacao, usuario)
            
            elif intent == "ptc_fluxo":
                return self._fluxo_ptc(interpretacao, usuario)
            
            elif intent == "pergunta":
                return self._fluxo_pergunta(interpretacao, usuario)
            
            elif intent == "saudacao":
                return self._fluxo_saudacao(interpretacao, usuario)
            
            elif intent == "ajuda":
                return self._fluxo_ajuda(interpretacao, usuario)
            
            else:
                return self._fluxo_mensagem_livre(interpretacao, usuario)
                
        except Exception as e:
            logger.error(f"Erro ao executar fluxo {intent}: {str(e)}")
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."
    
    def _fluxo_agendamento(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de agendamento"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        if nome:
            return f"Olá {nome}! Posso ajudar com agendamentos. Em breve teremos integração completa com agenda. Por enquanto, entre em contato pelo telefone (11) 99999-9999."
        else:
            return f"Olá! Posso ajudar com agendamentos. Em breve teremos integração completa com agenda. Por enquanto, entre em contato pelo telefone (11) 99999-9999."
    
    def _fluxo_ptc(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo PTC 2025 - Integrado com Knowledge Base"""
        mensagem = interpretacao["mensagem_original"]
        aula_numero = interpretacao.get("aula_numero")
        
        # Buscar na Knowledge Base (simulado - integrar com PostgreSQL real)
        if aula_numero:
            contexto = f"Pergunta sobre Aula {aula_numero} do PTC 2025"
        else:
            contexto = "Pergunta geral sobre PTC 2025"
        
        # Chamar GPT-5 com contexto
        resposta = self._chamar_gpt5(
            mensagem=mensagem,
            contexto=contexto,
            persona=interpretacao.get("persona")
        )
        
        return resposta
    
    def _fluxo_pergunta(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de perguntas gerais"""
        mensagem = interpretacao["mensagem_original"]
        
        # Chamar GPT-5 para responder
        resposta = self._chamar_gpt5(
            mensagem=mensagem,
            contexto="Pergunta geral",
            persona=interpretacao.get("persona")
        )
        
        return resposta
    
    def _fluxo_saudacao(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de saudação"""
        persona = interpretacao.get("persona", {})
        nome = persona.get("identificacao", {}).get("nome", "")
        
        if nome:
            return f"Olá {nome}! 👋 Como posso ajudar você hoje?"
        else:
            return "Olá! 👋 Sou o AI9, assistente inteligente da FT9. Como posso ajudar você hoje?"
    
    def _fluxo_ajuda(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de ajuda"""
        return """🤖 **AI9 - Assistente FT9 Intelligence**

Posso ajudar você com:

📅 **Agendamentos** - Marcar consultas e horários
📚 **PTC 2025** - Responder dúvidas sobre o curso
❓ **Perguntas** - Responder suas dúvidas gerais
💬 **Conversação** - Conversar naturalmente

Como posso ajudar você hoje?"""
    
    def _fluxo_mensagem_livre(self, interpretacao: Dict, usuario: str) -> str:
        """Fluxo de mensagem livre"""
        mensagem = interpretacao["mensagem_original"]
        
        # Chamar GPT-5 para resposta natural
        resposta = self._chamar_gpt5(
            mensagem=mensagem,
            contexto="Conversação livre",
            persona=interpretacao.get("persona")
        )
        
        return resposta
    
    def _chamar_gpt5(
        self, 
        mensagem: str, 
        contexto: str, 
        persona: Optional[Dict] = None
    ) -> str:
        """
        Chama GPT-5 para gerar resposta
        
        Args:
            mensagem: Mensagem do usuário
            contexto: Contexto da conversa
            persona: Dados da persona do usuário
            
        Returns:
            Resposta gerada pelo GPT-5
        """
        try:
            # Construir prompt com contexto e persona
            system_prompt = self._construir_system_prompt(persona)
            
            # Chamar API OpenAI
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4.1-mini",  # Usar modelo disponível no Manus
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{contexto}\n\n{mensagem}"}
                ],
                "max_completion_tokens": 500
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
                logger.info("Resposta GPT-5 gerada com sucesso")
                return resposta
            else:
                logger.error(f"Erro na API OpenAI: {response.status_code}")
                return "Desculpe, não consegui processar sua mensagem no momento."
                
        except Exception as e:
            logger.error(f"Erro ao chamar GPT-5: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."
    
    def _construir_system_prompt(self, persona: Optional[Dict] = None) -> str:
        """
        Constrói o system prompt para GPT-5
        
        Args:
            persona: Dados da persona do usuário
            
        Returns:
            System prompt personalizado
        """
        # Prompt base AI9
        prompt = """Você é o AI9, assistente inteligente da FT9 Intelligence.

Você foi desenvolvido com base na metodologia dos 9 Pilares do Empreendedorismo de Felipe Teixeira, especializada em empreendedorismo para área de saúde.

Características:
- Profissional mas acessível
- Objetivo e direto
- Baseado em dados reais
- Transparente sobre limitações
- Focado em resultados

Responda de forma natural, clara e útil."""
        
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
