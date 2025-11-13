"""
Sales Flow - Fluxo de Vendas e Conversão
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Conduzir o lead através do processo de vendas até a conversão
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SalesFlow:
    """
    Fluxo de vendas e conversão
    
    Etapas:
    1. Apresentação de soluções
    2. Demonstração de valor
    3. Apresentação de preços
    4. Tratamento de objeções iniciais
    5. Direcionamento para fechamento
    """
    
    def __init__(self, memory_engine, gpt_caller):
        """
        Inicializa o fluxo de vendas
        
        Args:
            memory_engine: Instância do FT9Memory
            gpt_caller: Função para chamar GPT
        """
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        logger.info("SalesFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """
        Detecta se a mensagem deve acionar o fluxo de vendas
        
        Args:
            interpretacao: Dict com intenção e metadados
            
        Returns:
            True se deve acionar este fluxo
        """
        intent = interpretacao.get("intencao", "")
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        # Triggers para vendas
        triggers = [
            "preço",
            "valor",
            "quanto custa",
            "investimento",
            "plano",
            "pacote",
            "como funciona",
            "quero contratar",
            "tenho interesse",
        ]
        
        if intent in ["interesse_comercial", "consulta_preco", "informacao_servico"]:
            return True
        
        if any(trigger in mensagem for trigger in triggers):
            return True
        
        return False
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """
        Executa o fluxo de vendas
        
        Args:
            interpretacao: Dict com intenção e metadados
            usuario: Identificador do usuário
            
        Returns:
            Resposta processada
        """
        try:
            mensagem = interpretacao.get("mensagem_original", "")
            persona = interpretacao.get("persona", {})
            identificacao = persona.get("identificacao", {})
            nome = identificacao.get("nome", "")
            
            # Detecta etapa específica
            if self._perguntou_preco(mensagem):
                return self._apresentar_precos(nome)
            
            if self._perguntou_como_funciona(mensagem):
                return self._explicar_funcionamento(nome)
            
            if self._demonstrou_interesse(mensagem):
                return self._conduzir_fechamento(nome)
            
            # Resposta personalizada com GPT
            return self._resposta_personalizada(interpretacao, usuario)
            
        except Exception as e:
            logger.error(f"Erro no SalesFlow: {str(e)}")
            return "Desculpe, ocorreu um erro. Pode repetir sua pergunta?"
    
    def _perguntou_preco(self, mensagem: str) -> bool:
        """Detecta se perguntou sobre preço"""
        palavras_preco = ["preço", "valor", "quanto custa", "investimento", "pagar"]
        return any(palavra in mensagem.lower() for palavra in palavras_preco)
    
    def _perguntou_como_funciona(self, mensagem: str) -> bool:
        """Detecta se perguntou como funciona"""
        palavras_funcionamento = ["como funciona", "funciona", "como é", "como seria"]
        return any(palavra in mensagem.lower() for palavra in palavras_funcionamento)
    
    def _demonstrou_interesse(self, mensagem: str) -> bool:
        """Detecta se demonstrou interesse em contratar"""
        palavras_interesse = ["quero", "tenho interesse", "gostaria", "vou contratar", "fechar"]
        return any(palavra in mensagem.lower() for palavra in palavras_interesse)
    
    def _apresentar_precos(self, nome: str) -> str:
        """Apresenta tabela de preços"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}excelente pergunta! 💰

Nossos planos são pensados para oferecer o melhor custo-benefício:

**🩺 CONSULTA AVULSA**
→ R$ 150,00 por sessão
→ Ideal para avaliação inicial

**📦 PACOTE 10 SESSÕES**
→ R$ 1.200,00 (R$ 120/sessão)
→ Economia de 20%
→ Validade: 3 meses

**⭐ PTC 2025 - PROGRAMA COMPLETO**
→ R$ 997,00/mês
→ Sessões ilimitadas
→ Acompanhamento contínuo
→ Suporte via WhatsApp
→ Acesso ao app FT9
→ **Melhor custo-benefício!**

Qual opção faz mais sentido para você?"""
    
    def _explicar_funcionamento(self, nome: str) -> str:
        """Explica como funciona o serviço"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}vou te explicar como funciona! 📋

**PASSO A PASSO:**

1️⃣ **AVALIAÇÃO INICIAL**
   → Consulta de 60min
   → Análise completa
   → Plano personalizado

2️⃣ **TRATAMENTO**
   → Sessões de 50min
   → Técnicas avançadas
   → Acompanhamento contínuo

3️⃣ **ACOMPANHAMENTO**
   → Suporte via WhatsApp
   → Ajustes no plano
   → Evolução monitorada

4️⃣ **RESULTADOS**
   → Melhora progressiva
   → Qualidade de vida
   → Prevenção de recaídas

**DIFERENCIAIS FT9:**
✅ Atendimento humanizado
✅ Tecnologia de ponta
✅ Equipe especializada
✅ Resultados comprovados

Quer agendar sua avaliação inicial?"""
    
    def _conduzir_fechamento(self, nome: str) -> str:
        """Conduz para fechamento"""
        saudacao = f"Que ótimo, {nome}! " if nome else "Que ótimo! "
        
        return f"""{saudacao}🎉

Vou te ajudar a dar esse passo importante para sua saúde!

Para finalizarmos, preciso confirmar alguns dados:

📱 **Telefone:** (já tenho)
📧 **E-mail:** Qual seu melhor e-mail?
📍 **Unidade:** Qual unidade prefere?
   → FT9 Moema
   → FT9 Pinheiros
   → FT9 Itaim

Depois disso, vou te passar para nossa equipe finalizar o agendamento e pagamento. Tudo bem assim?"""
    
    def _resposta_personalizada(self, interpretacao: Dict, usuario: str) -> str:
        """Gera resposta personalizada com GPT"""
        mensagem = interpretacao.get("mensagem_original", "")
        persona = interpretacao.get("persona", {})
        
        contexto = """Você é o AI9, assistente de vendas da FT9 Intelligence.

Sua missão:
1. Apresentar soluções de forma consultiva
2. Destacar benefícios, não apenas características
3. Criar senso de urgência sutil
4. Conduzir para fechamento
5. Ser empático e profissional

TABELA DE PREÇOS:
- Consulta avulsa: R$ 150
- Pacote 10 sessões: R$ 1.200 (20% desconto)
- PTC 2025: R$ 997/mês (ilimitado)

Use técnicas de vendas consultivas e sempre conduza para o próximo passo."""
        
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
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        # Se levantou objeção, vai para ObjectionsFlow
        objecoes = ["caro", "muito caro", "não tenho", "não posso", "vou pensar", "depois"]
        if any(obj in mensagem for obj in objecoes):
            return "objections_flow"
        
        # Se perguntou sobre PTC, vai para PTCFlow
        if "ptc" in mensagem or "programa" in mensagem:
            return "ptc_flow"
        
        # Se demonstrou interesse em fechar, vai para ClosingFlow
        if any(palavra in mensagem for palavra in ["quero", "vou fechar", "pode agendar"]):
            return "closing_flow"
        
        # Continua no sales
        return None
