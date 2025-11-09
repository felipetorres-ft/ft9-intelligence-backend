"""
FT9 WhatsApp Integration - AI Processing Module
Integrates with OpenAI for intelligent message processing
"""
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI processor using OpenAI for intelligent responses"""
    
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
    
    async def process_message(
        self,
        user_message: str,
        user_phone: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a user message and generate an AI response
        
        Args:
            user_message: The message text from the user
            user_phone: User's phone number (for context/logging)
            conversation_history: Optional list of previous messages
        
        Returns:
            AI-generated response text
        """
        try:
            # Build conversation context
            messages = [{"role": "system", "content": self.system_prompt}]
            
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
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            logger.info(f"AI response generated for user {user_phone}")
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
                max_tokens=200
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
