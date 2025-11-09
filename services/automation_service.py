"""
Serviço de Automações (FT9-Flow)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import json

logger = logging.getLogger(__name__)


class AutomationService:
    """
    Serviço para gerenciar automações e workflows
    """
    
    # Tipos de triggers
    TRIGGER_TYPES = [
        "message_received",      # Mensagem recebida no WhatsApp
        "scheduled",             # Agendamento (cron)
        "webhook",               # Webhook externo
        "payment_succeeded",     # Pagamento bem-sucedido
        "payment_failed",        # Falha no pagamento
        "subscription_created",  # Assinatura criada
        "conversation_started",  # Nova conversa iniciada
        "conversation_ended"     # Conversa finalizada
    ]
    
    # Tipos de ações
    ACTION_TYPES = [
        "send_whatsapp_message",  # Enviar mensagem WhatsApp
        "send_email",             # Enviar email
        "create_knowledge",       # Adicionar à base de conhecimento
        "call_webhook",           # Chamar webhook externo
        "wait",                   # Aguardar X tempo
        "conditional",            # Condição if/else
        "loop",                   # Loop sobre lista
        "ai_generate"             # Gerar resposta com IA
    ]
    
    async def create_automation(
        self,
        db: AsyncSession,
        organization_id: int,
        name: str,
        trigger_type: str,
        trigger_config: Dict[str, Any],
        actions: List[Dict[str, Any]],
        conditions: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None
    ) -> int:
        """
        Criar nova automação
        """
        try:
            from database.automation_models import Automation
            
            # Validar trigger type
            if trigger_type not in self.TRIGGER_TYPES:
                raise ValueError(f"Tipo de trigger inválido: {trigger_type}")
            
            # Criar automação
            automation = Automation(
                organization_id=organization_id,
                name=name,
                description=description,
                trigger_type=trigger_type,
                trigger_config=trigger_config,
                conditions=conditions or [],
                actions=actions,
                is_active=True
            )
            
            db.add(automation)
            await db.commit()
            await db.refresh(automation)
            
            logger.info(f"Automação criada: ID {automation.id}")
            
            return automation.id
        
        except Exception as e:
            logger.error(f"Erro ao criar automação: {e}")
            await db.rollback()
            raise
    
    async def execute_automation(
        self,
        db: AsyncSession,
        automation_id: int,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executar automação
        """
        try:
            from database.automation_models import Automation, AutomationExecution
            
            # Buscar automação
            result = await db.execute(
                select(Automation).where(Automation.id == automation_id)
            )
            automation = result.scalar_one_or_none()
            
            if not automation or not automation.is_active:
                raise ValueError("Automação não encontrada ou inativa")
            
            # Criar registro de execução
            execution = AutomationExecution(
                automation_id=automation_id,
                status="running",
                input_data=input_data
            )
            
            db.add(execution)
            await db.flush()
            
            try:
                # Avaliar condições
                if automation.conditions:
                    if not self._evaluate_conditions(automation.conditions, input_data):
                        execution.status = "skipped"
                        execution.completed_at = datetime.utcnow()
                        await db.commit()
                        return {"status": "skipped", "reason": "Conditions not met"}
                
                # Executar ações
                output_data = await self._execute_actions(
                    db=db,
                    actions=automation.actions,
                    context=input_data
                )
                
                # Atualizar execução
                execution.status = "completed"
                execution.output_data = output_data
                execution.completed_at = datetime.utcnow()
                
                # Atualizar automação
                automation.last_executed_at = datetime.utcnow()
                automation.execution_count += 1
                
                await db.commit()
                
                logger.info(f"Automação {automation_id} executada com sucesso")
                
                return {
                    "status": "completed",
                    "execution_id": execution.id,
                    "output": output_data
                }
            
            except Exception as e:
                execution.status = "failed"
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
                await db.commit()
                
                logger.error(f"Erro ao executar automação {automation_id}: {e}")
                raise
        
        except Exception as e:
            logger.error(f"Erro ao executar automação: {e}")
            raise
    
    def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """
        Avaliar condições (if/else)
        """
        for condition in conditions:
            operator = condition.get("operator")
            field = condition.get("field")
            value = condition.get("value")
            
            context_value = context.get(field)
            
            if operator == "equals":
                if context_value != value:
                    return False
            elif operator == "not_equals":
                if context_value == value:
                    return False
            elif operator == "contains":
                if value not in str(context_value):
                    return False
            elif operator == "greater_than":
                if not (context_value > value):
                    return False
            elif operator == "less_than":
                if not (context_value < value):
                    return False
        
        return True
    
    async def _execute_actions(
        self,
        db: AsyncSession,
        actions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executar lista de ações
        """
        results = []
        
        for action in actions:
            action_type = action.get("type")
            action_config = action.get("config", {})
            
            try:
                if action_type == "send_whatsapp_message":
                    result = await self._action_send_whatsapp(action_config, context)
                elif action_type == "send_email":
                    result = await self._action_send_email(action_config, context)
                elif action_type == "create_knowledge":
                    result = await self._action_create_knowledge(db, action_config, context)
                elif action_type == "call_webhook":
                    result = await self._action_call_webhook(action_config, context)
                elif action_type == "wait":
                    result = await self._action_wait(action_config)
                elif action_type == "ai_generate":
                    result = await self._action_ai_generate(action_config, context)
                else:
                    result = {"status": "skipped", "reason": f"Unknown action type: {action_type}"}
                
                results.append({
                    "action_type": action_type,
                    "result": result
                })
            
            except Exception as e:
                logger.error(f"Erro ao executar ação {action_type}: {e}")
                results.append({
                    "action_type": action_type,
                    "error": str(e)
                })
        
        return {"actions_executed": len(results), "results": results}
    
    async def _action_send_whatsapp(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ação: Enviar mensagem WhatsApp
        """
        from whatsapp_client import WhatsAppClient
        
        client = WhatsAppClient()
        
        to = config.get("to") or context.get("phone_number")
        message = config.get("message", "").format(**context)
        
        await client.send_message(to, message)
        
        return {"status": "sent", "to": to}
    
    async def _action_send_email(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ação: Enviar email
        """
        # TODO: Implementar envio de email
        return {"status": "not_implemented"}
    
    async def _action_create_knowledge(
        self,
        db: AsyncSession,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ação: Adicionar à base de conhecimento
        """
        from services import rag_service
        
        organization_id = context.get("organization_id")
        title = config.get("title", "").format(**context)
        content = config.get("content", "").format(**context)
        
        knowledge_id = await rag_service.add_knowledge(
            db=db,
            organization_id=organization_id,
            title=title,
            content=content
        )
        
        return {"status": "created", "knowledge_id": knowledge_id}
    
    async def _action_call_webhook(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ação: Chamar webhook externo
        """
        import httpx
        
        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})
        body = config.get("body", {})
        
        # Substituir variáveis no body
        body_str = json.dumps(body).format(**context)
        body = json.loads(body_str)
        
        async with httpx.AsyncClient() as client:
            if method == "POST":
                response = await client.post(url, json=body, headers=headers)
            elif method == "GET":
                response = await client.get(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            return {
                "status": "called",
                "status_code": response.status_code,
                "response": response.text
            }
    
    async def _action_wait(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ação: Aguardar
        """
        import asyncio
        
        seconds = config.get("seconds", 0)
        await asyncio.sleep(seconds)
        
        return {"status": "waited", "seconds": seconds}
    
    async def _action_ai_generate(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ação: Gerar resposta com IA
        """
        from openai import OpenAI
        
        client = OpenAI()
        
        prompt = config.get("prompt", "").format(**context)
        model = config.get("model", "gpt-4.1-mini")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        return {"status": "generated", "answer": answer}


# Instância global do serviço
automation_service = AutomationService()
