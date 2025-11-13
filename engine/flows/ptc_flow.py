"""
PTC Flow - Fluxo do Programa de Tratamento Contínuo 2025
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Gerenciar jornada PTC, recorrência e acompanhamento contínuo
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PTCFlow:
    """
    Fluxo PTC 2025 - Programa de Tratamento Contínuo
    
    Funcionalidades:
    1. Apresentação do programa
    2. Onboarding de novos pacientes PTC
    3. Acompanhamento de recorrência
    4. Lembretes de sessões
    5. Expansão familiar
    """
    
    def __init__(self, memory_engine, gpt_caller):
        """
        Inicializa o fluxo PTC
        
        Args:
            memory_engine: Instância do FT9Memory
            gpt_caller: Função para chamar GPT
        """
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("PTCFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """
        Detecta se a mensagem deve acionar o fluxo PTC
        
        Args:
            interpretacao: Dict com intenção e metadados
            
        Returns:
            True se deve acionar este fluxo
        """
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        triggers = [
            "ptc",
            "programa",
            "tratamento contínuo",
            "acompanhamento",
            "recorrência",
            "manutenção",
            "preventivo",
        ]
        
        if any(trigger in mensagem for trigger in triggers):
            return True
        
        # Verifica se é paciente PTC ativo
        persona = interpretacao.get("persona", {})
        if persona.get("ptc_ativo", False):
            return True
        
        return False
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """
        Executa o fluxo PTC
        
        Args:
            interpretacao: Dict com intenção e metadados
            usuario: Identificador do usuário
            
        Returns:
            Resposta processada
        """
        try:
            persona = interpretacao.get("persona", {})
            ptc_ativo = persona.get("ptc_ativo", False)
            
            if not ptc_ativo:
                # Apresenta o programa PTC
                return self._apresentar_ptc(persona)
            else:
                # Acompanhamento de paciente PTC ativo
                return self._acompanhar_ptc(interpretacao, usuario)
            
        except Exception as e:
            logger.error(f"Erro no PTCFlow: {str(e)}")
            return "Desculpe, ocorreu um erro. Pode repetir?"
    
    def _apresentar_ptc(self, persona: Dict) -> str:
        """Apresenta o programa PTC 2025"""
        identificacao = persona.get("identificacao", {})
        nome = identificacao.get("nome", "")
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}deixa eu te apresentar o **PTC 2025** - nosso programa mais completo! ⭐

**O QUE É O PTC 2025?**

É um **Programa de Tratamento Contínuo** que vai além da fisioterapia tradicional:

🔄 **SESSÕES ILIMITADAS**
→ Venha quantas vezes precisar
→ Sem limite mensal
→ Flexibilidade total

🎯 **ACOMPANHAMENTO PERSONALIZADO**
→ Plano individual
→ Evolução monitorada
→ Ajustes contínuos

🤖 **TECNOLOGIA AI9**
→ Suporte 24/7 via WhatsApp
→ Lembretes inteligentes
→ Dicas personalizadas

👨‍👩‍👧‍👦 **EXPANSÃO FAMILIAR**
→ Traga sua família
→ Descontos progressivos
→ Saúde para todos

📊 **RESULTADOS MENSURÁVEIS**
→ Avaliações periódicas
→ Métricas de evolução
→ Relatórios detalhados

**INVESTIMENTO:**
R$ 997/mês - Sem fidelidade

**GARANTIA:**
30 dias de satisfação ou seu dinheiro de volta

Quer saber mais sobre algum ponto específico?"""
    
    def _acompanhar_ptc(self, interpretacao: Dict, usuario: str) -> str:
        """Acompanha paciente PTC ativo"""
        mensagem = interpretacao.get("mensagem_original", "")
        persona = interpretacao.get("persona", {})
        
        # Usa GPT com contexto PTC
        contexto = """Você é o AI9, assistente de acompanhamento PTC 2025.

O paciente é um membro ativo do PTC. Sua missão:
1. Acompanhar evolução do tratamento
2. Lembrar de sessões agendadas
3. Sugerir retornos quando necessário
4. Oferecer suporte e orientações
5. Identificar oportunidades de expansão familiar

Seja proativo, empático e focado em resultados.
Sempre pergunte sobre a evolução e ofereça ajuda."""
        
        resposta = self.gpt_caller(
            mensagem=mensagem,
            contexto=contexto,
            persona=persona
        )
        
        return resposta
    
    def verificar_recorrencia(self, usuario: str) -> Optional[str]:
        """
        Verifica se precisa acionar recorrência
        
        Args:
            usuario: Identificador do usuário
            
        Returns:
            Mensagem de recorrência ou None
        """
        # TODO: Integrar com banco de dados para verificar:
        # - Última sessão
        # - Sessões agendadas
        # - Tempo desde última visita
        
        # Exemplo de lógica:
        # if dias_desde_ultima_sessao > 7:
        #     return self._mensagem_retorno()
        
        return None
    
    def _mensagem_retorno(self) -> str:
        """Mensagem de retorno para paciente inativo"""
        return """Oi! Tudo bem? 😊

Percebi que faz um tempinho que você não vem para sua sessão.

Como você está se sentindo? A dor melhorou ou voltou?

Lembro que no PTC 2025 é importante manter a **regularidade** para:
✅ Consolidar os ganhos
✅ Prevenir recaídas
✅ Manter qualidade de vida

Que tal agendar sua próxima sessão? Tenho horários disponíveis essa semana!"""
    
    def sugerir_expansao_familiar(self, persona: Dict) -> str:
        """Sugere expansão familiar"""
        identificacao = persona.get("identificacao", {})
        nome = identificacao.get("nome", "")
        
        return f"""Oi {nome}! 👋

Vi que você está tendo ótimos resultados no PTC 2025! Que alegria! 🎉

Você sabia que pode **trazer sua família** para o programa?

**BENEFÍCIOS DA EXPANSÃO FAMILIAR:**

💰 **DESCONTOS PROGRESSIVOS**
→ 2 pessoas: 10% desconto
→ 3 pessoas: 15% desconto
→ 4+ pessoas: 20% desconto

👨‍👩‍👧‍👦 **SAÚDE PARA TODOS**
→ Prevenção desde cedo
→ Qualidade de vida familiar
→ Acompanhamento integrado

🎯 **HORÁRIOS SINCRONIZADOS**
→ Venham juntos
→ Otimização de tempo
→ Mais praticidade

Alguém da sua família tem interesse? Posso fazer uma avaliação gratuita!"""
    
    def proximo_fluxo(self, interpretacao: Dict) -> Optional[str]:
        """
        Determina qual deve ser o próximo fluxo
        
        Args:
            interpretacao: Dict com intenção e metadados
            
        Returns:
            Nome do próximo fluxo ou None
        """
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        # Se quer contratar, vai para ClosingFlow
        if any(palavra in mensagem for palavra in ["quero", "contratar", "fechar", "assinar"]):
            return "closing_flow"
        
        # Se tem dúvida sobre preço, volta para SalesFlow
        if any(palavra in mensagem for palavra in ["preço", "valor", "quanto"]):
            return "sales_flow"
        
        # Se mencionou família, vai para FamilyFlow
        if any(palavra in mensagem for palavra in ["família", "esposa", "marido", "filho", "filha", "pai", "mãe"]):
            return "family_flow"
        
        return None
