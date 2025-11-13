"""
Closing Flow - Fluxo de Fechamento e Conversão
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Finalizar conversão e agendar primeira sessão
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ClosingFlow:
    """Fluxo de fechamento e conversão"""
    
    def __init__(self, memory_engine, gpt_caller):
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("ClosingFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """Detecta intenção de fechar"""
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        triggers = ["quero", "vou fechar", "pode agendar", "vamos", "fechado", 
                   "confirmo", "aceito", "topo"]
        
        return any(trigger in mensagem for trigger in triggers)
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """Executa fluxo de fechamento"""
        persona = interpretacao.get("persona", {})
        identificacao = persona.get("identificacao", {})
        nome = identificacao.get("nome", "")
        telefone = identificacao.get("telefone", "")
        
        if not nome or not telefone:
            return self._coletar_dados_finais()
        
        return self._finalizar_conversao(nome, telefone)
    
    def _coletar_dados_finais(self) -> str:
        """Coleta dados finais para fechamento"""
        return """Perfeito! Vamos finalizar então! 🎉

Para agendar, preciso confirmar alguns dados:

📝 **DADOS PARA AGENDAMENTO:**

1️⃣ **Nome completo:**
2️⃣ **Telefone:**
3️⃣ **E-mail:**
4️⃣ **CPF:** (para cadastro)

5️⃣ **Unidade preferida:**
   → FT9 Moema
   → FT9 Pinheiros
   → FT9 Itaim

6️⃣ **Melhor dia/horário:**
   → Manhã (8h-12h)
   → Tarde (13h-18h)
   → Noite (18h-21h)

Pode me passar essas informações?"""
    
    def _finalizar_conversao(self, nome: str, telefone: str) -> str:
        """Finaliza conversão"""
        return f"""🎉 **PARABÉNS, {nome.upper()}!**

Você acabou de dar um passo importante para sua saúde!

**PRÓXIMOS PASSOS:**

✅ **AGORA:**
→ Vou registrar seu interesse
→ Nossa equipe vai te ligar em até 30min
→ Você receberá confirmação por WhatsApp

📅 **AGENDAMENTO:**
→ Escolha de data/horário
→ Confirmação de unidade
→ Envio de localização

💳 **PAGAMENTO:**
→ Link para pagamento seguro
→ Opções de parcelamento
→ Confirmação automática

📱 **ACESSO:**
→ Login no app FT9
→ Acesso ao AI9 24/7
→ Materiais exclusivos

**IMPORTANTE:**
Fique de olho no WhatsApp! Nossa equipe vai entrar em contato em breve.

Enquanto isso, tem alguma dúvida que eu possa esclarecer?

Bem-vindo(a) à família FT9! 🚀"""
    
    def notificar_equipe(self, usuario: str, dados: Dict) -> bool:
        """
        Notifica equipe sobre novo lead convertido
        
        Args:
            usuario: Identificador do usuário
            dados: Dados do lead
            
        Returns:
            True se notificação foi enviada
        """
        # TODO: Integrar com sistema de notificações
        # - Enviar para CRM
        # - Notificar equipe de vendas
        # - Criar tarefa de follow-up
        
        logger.info(f"Lead convertido: {usuario} - {dados}")
        return True
    
    def proximo_fluxo(self, interpretacao: Dict) -> Optional[str]:
        """Não há próximo fluxo - conversão finalizada"""
        return None
