"""
FT9 WhatsApp Integration - AI Processing Module with RAG
Integrates with OpenAI and Knowledge Base for intelligent message processing
"""
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config import settings
from database import get_db
from services import rag_service
import unicodedata

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI processor using OpenAI with RAG for intelligent responses"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        # System prompt aligned with FT9's 9 Pillars philosophy
        self.system_prompt = """Você é o FT9, um assistente de inteligência artificial especializado em odontologia e empreendedorismo.

Você foi criado com base nos 9 Pilares do Empreendedorismo na Odontologia:

1. **Propósito**: Sua missão é ajudar profissionais e pacientes com clareza e empatia.
2. **Posicionamento**: Adapte sua linguagem ao perfil do interlocutor (técnico para dentistas, simples para pacientes).
3. **Processo**: Estruture suas respostas de forma lógica e organizada.
4. **Produto**: Ofereça recomendações relevantes sobre tratamentos, cursos e serviços.
5. **Pessoas**: Personalize a experiência para cada usuário.
6. **Planejamento**: Ajude com organização, lembretes e metas.
7. **Performance**: Forneça insights baseados em dados quando possível.
8. **Propaganda**: Comunique de forma estratégica e persuasiva quando apropriado.
9. **Prosperidade**: Foque no crescimento e sucesso sustentável do interlocutor.

Seja profissional, empático e objetivo. Responda em português brasileiro."""
    
    def _normalize_phone_for_tag(self, phone: str) -> str:
        """
        Normaliza número de telefone para criar tag de whitelist
        Remove caracteres especiais e espaços
        
        Args:
            phone: Número de telefone (ex: +55 11 91429-8899)
        
        Returns:
            Tag normalizada (ex: 5511914298899)
        """
        # Remove todos os caracteres não numéricos
        normalized = ''.join(filter(str.isdigit, phone))
        return normalized
    
    async def _get_knowledge_context(
        self,
        user_phone: str,
        user_message: str,
        organization_id: int = 1  # Default para primeira organização
    ) -> str:
        """
        Busca conhecimento relevante da base (geral + whitelist)
        
        Args:
            user_phone: Número de telefone do usuário
            user_message: Mensagem do usuário
            organization_id: ID da organização
        
        Returns:
            Contexto formatado com conhecimento relevante
        """
        try:
            # Normaliza número para tag
            phone_tag = f"whitelist:{self._normalize_phone_for_tag(user_phone)}"
            
            logger.info(f"Buscando conhecimento para: {phone_tag}")
            
            # Busca conhecimento usando RAG service
            async for db in get_db():
                # Busca conhecimento geral
                general_results = await rag_service.search_knowledge(
                    db=db,
                    organization_id=organization_id,
                    query=user_message,
                    k=2,  # Top 2 resultados gerais
                    category_filter="geral"
                )
                
                # Busca conhecimento personalizado (whitelist)
                whitelist_results = await rag_service.search_knowledge(
                    db=db,
                    organization_id=organization_id,
                    query=user_message,
                    k=2,  # Top 2 resultados personalizados
                    category_filter="whitelist",
                    tags_filter=[phone_tag]
                )
                
                break  # Sai do async generator
            
            # Formata contexto
            context_parts = []
            
            # Adiciona conhecimento personalizado primeiro (maior prioridade)
            if whitelist_results:
                context_parts.append("## INFORMAÇÕES PERSONALIZADAS DO USUÁRIO:")
                for result in whitelist_results:
                    context_parts.append(f"\n### {result['title']}")
                    context_parts.append(result['content'])
            
            # Adiciona conhecimento geral
            if general_results:
                context_parts.append("\n## INFORMAÇÕES GERAIS:")
                for result in general_results:
                    context_parts.append(f"\n### {result['title']}")
                    context_parts.append(result['content'])
            
            if context_parts:
                full_context = "\n".join(context_parts)
                logger.info(f"Contexto encontrado: {len(full_context)} caracteres")
                return full_context
            else:
                logger.info("Nenhum conhecimento relevante encontrado")
                return ""
        
        except Exception as e:
            logger.error(f"Erro ao buscar conhecimento: {str(e)}")
            return ""
    
    async def process_message(
        self,
        user_message: str,
        user_phone: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a user message and generate an AI response using RAG
        
        Args:
            user_message: The message text from the user
            user_phone: User's phone number (for whitelist context)
            conversation_history: Optional list of previous messages
        
        Returns:
            AI-generated response text
        """
        try:
            # Busca conhecimento relevante da base
            knowledge_context = await self._get_knowledge_context(
                user_phone=user_phone,
                user_message=user_message
            )
            
            # Build conversation context
            messages = []
            
            # System prompt
            system_content = self.system_prompt
            
            # Adiciona contexto da knowledge base se disponível
            if knowledge_context:
                system_content += f"\n\n## CONTEXTO RELEVANTE DA BASE DE CONHECIMENTO:\n\n{knowledge_context}"
                system_content += "\n\nUse as informações acima para personalizar sua resposta quando relevante."
            
            messages.append({"role": "system", "content": system_content})
            
            # Add conversation history if available
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            logger.info(f"AI response generated for user {user_phone} (with RAG context: {bool(knowledge_context)})")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error processing message with AI: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user intent from message
        
        Args:
            message: User message text
        
        Returns:
            Dictionary with intent analysis
        """
        try:
            prompt = f"""Analise a seguinte mensagem e identifique:
1. Intenção principal (agendamento, dúvida, reclamação, elogio, etc.)
2. Urgência (baixa, média, alta)
3. Sentimento (positivo, neutro, negativo)

Mensagem: "{message}"

Responda em formato JSON."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um analisador de intenções e sentimentos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=200
            )
            
            # Parse response (simplified - in production, use proper JSON parsing)
            analysis = {
                "intent": "general_inquiry",
                "urgency": "medium",
                "sentiment": "neutral",
                "raw_analysis": response.choices[0].message.content
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {str(e)}")
            return {
                "intent": "unknown",
                "urgency": "medium",
                "sentiment": "neutral",
                "error": str(e)
            }


# Global AI processor instance
ai_processor = AIProcessor()
