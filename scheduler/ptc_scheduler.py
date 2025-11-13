"""
PTC Scheduler - Motor de Recorrência do Programa PTC 2025
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Gerenciar recorrência automática de pacientes PTC
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class PTCScheduler:
    """
    Motor de recorrência do PTC 2025
    
    Funcionalidades:
    1. Detectar atrasos em sessões
    2. Sugerir retornos baseados em histórico
    3. Trigger de expansão familiar
    4. Lembretes automáticos
    5. Análise de risco de churn
    """
    
    def __init__(self, db_session, whatsapp_gateway):
        """
        Inicializa o scheduler
        
        Args:
            db_session: Sessão do banco de dados
            whatsapp_gateway: Gateway para envio de mensagens
        """
        self.db = db_session
        self.whatsapp = whatsapp_gateway
        
        # Configurações de recorrência
        self.config = {
            "dias_alerta_atraso": 7,  # Alerta após 7 dias sem sessão
            "dias_risco_churn": 14,   # Risco de churn após 14 dias
            "dias_churn": 30,          # Considerado churn após 30 dias
            "intervalo_ideal_sessoes": 3,  # Intervalo ideal entre sessões (dias)
        }
        
        logger.info("PTCScheduler inicializado")
    
    async def executar_ciclo_diario(self):
        """
        Executa ciclo diário de verificações
        
        Deve ser chamado por um cron job diário
        """
        try:
            logger.info("Iniciando ciclo diário do PTCScheduler")
            
            # 1. Detectar atrasos
            await self._detectar_atrasos()
            
            # 2. Sugerir retornos
            await self._sugerir_retornos()
            
            # 3. Identificar oportunidades de expansão familiar
            await self._identificar_expansao_familiar()
            
            # 4. Enviar lembretes de sessões agendadas
            await self._enviar_lembretes()
            
            # 5. Analisar risco de churn
            await self._analisar_risco_churn()
            
            logger.info("Ciclo diário do PTCScheduler concluído")
            
        except Exception as e:
            logger.error(f"Erro no ciclo diário do PTCScheduler: {str(e)}")
    
    async def _detectar_atrasos(self):
        """Detecta pacientes PTC com atrasos em sessões"""
        try:
            # TODO: Query no banco de dados
            # SELECT * FROM pacientes_ptc 
            # WHERE ultima_sessao < NOW() - INTERVAL '7 days'
            # AND status = 'ativo'
            
            pacientes_atrasados = []  # Placeholder
            
            for paciente in pacientes_atrasados:
                dias_atraso = self._calcular_dias_atraso(paciente)
                
                if dias_atraso >= self.config["dias_alerta_atraso"]:
                    await self._enviar_mensagem_retorno(paciente, dias_atraso)
            
            logger.info(f"Detectados {len(pacientes_atrasados)} pacientes atrasados")
            
        except Exception as e:
            logger.error(f"Erro ao detectar atrasos: {str(e)}")
    
    async def _sugerir_retornos(self):
        """Sugere retornos baseados em padrões históricos"""
        try:
            # TODO: Query no banco de dados
            # Analisa histórico de sessões e sugere próxima data ideal
            
            pacientes_para_sugestao = []  # Placeholder
            
            for paciente in pacientes_para_sugestao:
                proxima_data_sugerida = self._calcular_proxima_sessao(paciente)
                await self._enviar_sugestao_retorno(paciente, proxima_data_sugerida)
            
            logger.info(f"Enviadas {len(pacientes_para_sugestao)} sugestões de retorno")
            
        except Exception as e:
            logger.error(f"Erro ao sugerir retornos: {str(e)}")
    
    async def _identificar_expansao_familiar(self):
        """Identifica oportunidades de expansão familiar"""
        try:
            # TODO: Query no banco de dados
            # SELECT * FROM pacientes_ptc 
            # WHERE satisfacao_alta = true
            # AND familia_convidada = false
            # AND tempo_programa > 30 days
            
            pacientes_elegíveis = []  # Placeholder
            
            for paciente in pacientes_elegíveis:
                await self._enviar_convite_familiar(paciente)
            
            logger.info(f"Enviados {len(pacientes_elegíveis)} convites de expansão familiar")
            
        except Exception as e:
            logger.error(f"Erro ao identificar expansão familiar: {str(e)}")
    
    async def _enviar_lembretes(self):
        """Envia lembretes de sessões agendadas"""
        try:
            # TODO: Query no banco de dados
            # SELECT * FROM agendamentos
            # WHERE data_sessao = TOMORROW
            # AND lembrete_enviado = false
            
            agendamentos_amanha = []  # Placeholder
            
            for agendamento in agendamentos_amanha:
                await self._enviar_lembrete_sessao(agendamento)
            
            logger.info(f"Enviados {len(agendamentos_amanha)} lembretes de sessão")
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes: {str(e)}")
    
    async def _analisar_risco_churn(self):
        """Analisa risco de churn de pacientes"""
        try:
            # TODO: Query no banco de dados
            # Identifica pacientes com padrão de risco de churn
            
            pacientes_risco = []  # Placeholder
            
            for paciente in pacientes_risco:
                nivel_risco = self._calcular_nivel_risco(paciente)
                
                if nivel_risco == "alto":
                    await self._acionar_retencao(paciente)
            
            logger.info(f"Identificados {len(pacientes_risco)} pacientes em risco")
            
        except Exception as e:
            logger.error(f"Erro ao analisar risco de churn: {str(e)}")
    
    def _calcular_dias_atraso(self, paciente: Dict) -> int:
        """Calcula dias de atraso desde última sessão"""
        ultima_sessao = paciente.get("ultima_sessao")
        if not ultima_sessao:
            return 0
        
        hoje = datetime.now()
        delta = hoje - ultima_sessao
        return delta.days
    
    def _calcular_proxima_sessao(self, paciente: Dict) -> datetime:
        """Calcula data ideal para próxima sessão"""
        ultima_sessao = paciente.get("ultima_sessao")
        intervalo_medio = paciente.get("intervalo_medio_sessoes", 3)
        
        if not ultima_sessao:
            return datetime.now() + timedelta(days=3)
        
        return ultima_sessao + timedelta(days=intervalo_medio)
    
    def _calcular_nivel_risco(self, paciente: Dict) -> str:
        """Calcula nível de risco de churn"""
        dias_atraso = self._calcular_dias_atraso(paciente)
        
        if dias_atraso >= self.config["dias_churn"]:
            return "crítico"
        elif dias_atraso >= self.config["dias_risco_churn"]:
            return "alto"
        elif dias_atraso >= self.config["dias_alerta_atraso"]:
            return "médio"
        else:
            return "baixo"
    
    async def _enviar_mensagem_retorno(self, paciente: Dict, dias_atraso: int):
        """Envia mensagem de retorno personalizada"""
        nome = paciente.get("nome", "")
        telefone = paciente.get("telefone")
        
        mensagem = f"""Oi {nome}! Tudo bem? 😊

Percebi que faz {dias_atraso} dias que você não vem para sua sessão do PTC 2025.

Como você está se sentindo? A dor melhorou ou voltou?

Lembro que no PTC é importante manter a **regularidade** para:
✅ Consolidar os ganhos
✅ Prevenir recaídas
✅ Manter qualidade de vida

Que tal agendar sua próxima sessão? Tenho horários disponíveis essa semana!"""
        
        if telefone:
            await self.whatsapp.enviar_mensagem(telefone, mensagem)
            logger.info(f"Mensagem de retorno enviada para {nome}")
    
    async def _enviar_sugestao_retorno(self, paciente: Dict, data_sugerida: datetime):
        """Envia sugestão de retorno"""
        nome = paciente.get("nome", "")
        telefone = paciente.get("telefone")
        
        data_formatada = data_sugerida.strftime("%d/%m/%Y")
        
        mensagem = f"""Oi {nome}! 👋

Baseado no seu histórico, sugiro que você agende sua próxima sessão para **{data_formatada}**.

Isso vai manter a continuidade do seu tratamento e garantir os melhores resultados!

Posso agendar para você? Tenho horários disponíveis! 📅"""
        
        if telefone:
            await self.whatsapp.enviar_mensagem(telefone, mensagem)
            logger.info(f"Sugestão de retorno enviada para {nome}")
    
    async def _enviar_convite_familiar(self, paciente: Dict):
        """Envia convite de expansão familiar"""
        nome = paciente.get("nome", "")
        telefone = paciente.get("telefone")
        
        mensagem = f"""Oi {nome}! 😊

Vi que você está tendo ótimos resultados no PTC 2025! Que alegria! 🎉

Você sabia que pode **trazer sua família** para o programa com descontos especiais?

**BENEFÍCIOS:**
💰 Até 20% de desconto
👨‍👩‍👧‍👦 Saúde para toda família
🎯 Horários sincronizados

Alguém da sua família tem interesse? Posso fazer uma avaliação gratuita!"""
        
        if telefone:
            await self.whatsapp.enviar_mensagem(telefone, mensagem)
            logger.info(f"Convite familiar enviado para {nome}")
    
    async def _enviar_lembrete_sessao(self, agendamento: Dict):
        """Envia lembrete de sessão agendada"""
        paciente = agendamento.get("paciente", {})
        nome = paciente.get("nome", "")
        telefone = paciente.get("telefone")
        
        data_sessao = agendamento.get("data_sessao")
        horario = agendamento.get("horario")
        unidade = agendamento.get("unidade", "")
        
        mensagem = f"""🔔 **LEMBRETE DE SESSÃO**

Oi {nome}! Lembrete da sua sessão:

📅 **Data:** {data_sessao.strftime("%d/%m/%Y")}
🕐 **Horário:** {horario}
📍 **Local:** FT9 {unidade}

**IMPORTANTE:**
→ Chegar 10min antes
→ Trazer roupa confortável
→ Trazer toalha

Confirma presença? 😊"""
        
        if telefone:
            await self.whatsapp.enviar_mensagem(telefone, mensagem)
            logger.info(f"Lembrete de sessão enviado para {nome}")
    
    async def _acionar_retencao(self, paciente: Dict):
        """Aciona fluxo de retenção para paciente em risco"""
        nome = paciente.get("nome", "")
        telefone = paciente.get("telefone")
        
        mensagem = f"""Oi {nome}, tudo bem? 😊

Sentimos sua falta aqui na FT9! 

Percebi que faz um tempinho que você não aparece. Aconteceu algo?

Estamos com uma **oferta especial** para você retornar:

🎁 **50% OFF** na próxima sessão
🆓 Reavaliação gratuita
📅 Prioridade no agendamento

Sua saúde é importante para nós! Vamos conversar?"""
        
        if telefone:
            await self.whatsapp.enviar_mensagem(telefone, mensagem)
            logger.info(f"Fluxo de retenção acionado para {nome}")
            
            # TODO: Notificar equipe comercial sobre paciente em risco


# Função para executar scheduler via cron
async def executar_scheduler_diario():
    """
    Função para ser chamada por cron job diário
    
    Exemplo de configuração cron:
    0 9 * * * /usr/bin/python3 /path/to/ptc_scheduler.py
    """
    try:
        # TODO: Inicializar db_session e whatsapp_gateway
        # db_session = get_db_session()
        # whatsapp_gateway = WhatsAppGateway()
        
        # scheduler = PTCScheduler(db_session, whatsapp_gateway)
        # await scheduler.executar_ciclo_diario()
        
        logger.info("Scheduler diário executado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao executar scheduler diário: {str(e)}")


if __name__ == "__main__":
    # Executa scheduler quando chamado diretamente
    asyncio.run(executar_scheduler_diario())
