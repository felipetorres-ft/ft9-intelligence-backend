"""
Objections Flow - Fluxo de Tratamento de Objeções
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025

Objetivo: Identificar e tratar objeções de forma estruturada e empática
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ObjectionsFlow:
    """
    Fluxo de tratamento de objeções
    
    Objeções comuns:
    1. Preço ("muito caro", "não tenho dinheiro")
    2. Tempo ("vou pensar", "preciso conversar")
    3. Desconfiança ("não conheço", "não sei se funciona")
    4. Prioridade ("não é urgente", "depois eu vejo")
    5. Comparação ("vou ver outros lugares")
    """
    
    def __init__(self, memory_engine, gpt_caller):
        """
        Inicializa o fluxo de objeções
        
        Args:
            memory_engine: Instância do FT9Memory
            gpt_caller: Função para chamar GPT
        """
        self.memory = memory_engine
        self.gpt_caller = gpt_caller
        
        # Mapeamento de objeções → respostas estruturadas
        self.objecoes_map = {
            "preco": ["caro", "muito caro", "não tenho dinheiro", "não posso pagar", "valor alto"],
            "tempo": ["vou pensar", "preciso pensar", "vou ver", "depois", "mais tarde"],
            "desconfianca": ["não conheço", "não sei", "funciona mesmo", "é confiável"],
            "prioridade": ["não é urgente", "não preciso agora", "quando piorar"],
            "comparacao": ["vou ver outros", "vou pesquisar", "comparar preços"],
        }
        
        logger.info("ObjectionsFlow inicializado")
    
    def detectar(self, interpretacao: Dict[str, Any]) -> bool:
        """
        Detecta se a mensagem contém uma objeção
        
        Args:
            interpretacao: Dict com intenção e metadados
            
        Returns:
            True se detectou objeção
        """
        mensagem = interpretacao.get("mensagem_original", "").lower()
        
        # Verifica todas as objeções mapeadas
        for tipo, triggers in self.objecoes_map.items():
            if any(trigger in mensagem for trigger in triggers):
                return True
        
        return False
    
    def identificar_tipo(self, mensagem: str) -> str:
        """
        Identifica o tipo de objeção
        
        Args:
            mensagem: Mensagem do usuário
            
        Returns:
            Tipo da objeção
        """
        mensagem_lower = mensagem.lower()
        
        for tipo, triggers in self.objecoes_map.items():
            if any(trigger in mensagem_lower for trigger in triggers):
                return tipo
        
        return "geral"
    
    def executar(self, interpretacao: Dict[str, Any], usuario: str) -> str:
        """
        Executa o fluxo de tratamento de objeções
        
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
            
            # Identifica tipo de objeção
            tipo_objecao = self.identificar_tipo(mensagem)
            
            # Trata objeção específica
            if tipo_objecao == "preco":
                return self._tratar_objecao_preco(nome)
            
            elif tipo_objecao == "tempo":
                return self._tratar_objecao_tempo(nome)
            
            elif tipo_objecao == "desconfianca":
                return self._tratar_objecao_desconfianca(nome)
            
            elif tipo_objecao == "prioridade":
                return self._tratar_objecao_prioridade(nome)
            
            elif tipo_objecao == "comparacao":
                return self._tratar_objecao_comparacao(nome)
            
            else:
                return self._tratar_objecao_geral(interpretacao, usuario)
            
        except Exception as e:
            logger.error(f"Erro no ObjectionsFlow: {str(e)}")
            return "Entendo sua preocupação. Posso esclarecer melhor algum ponto específico?"
    
    def _tratar_objecao_preco(self, nome: str) -> str:
        """Trata objeção de preço"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}entendo perfeitamente sua preocupação com o investimento. 💰

Deixa eu te mostrar uma perspectiva diferente:

**QUANTO CUSTA NÃO TRATAR?**
→ Dor contínua afetando sua rotina
→ Perda de produtividade no trabalho
→ Medicamentos paliativos (sem resolver a causa)
→ Risco de agravamento do quadro

**NOSSO PTC 2025 (R$ 997/mês):**
→ Sessões ilimitadas
→ R$ 33/dia para sua saúde
→ Menos que um almoço por dia
→ **Investimento em qualidade de vida**

**OPÇÕES DE PAGAMENTO:**
✅ Parcelamento no cartão
✅ Desconto no débito/PIX
✅ Pacotes com desconto progressivo

Além disso, muitos planos de saúde reembolsam parte do valor. Quer que eu verifique se o seu cobre?"""
    
    def _tratar_objecao_tempo(self, nome: str) -> str:
        """Trata objeção de tempo (vou pensar)"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}claro, é importante pensar bem antes de decidir! 🤔

Mas deixa eu te fazer uma pergunta:

**O que você precisa saber para tomar essa decisão?**

Porque se for:
→ Dúvida sobre o tratamento → Posso explicar melhor
→ Dúvida sobre preço → Temos opções flexíveis
→ Dúvida sobre resultados → Temos casos de sucesso

A verdade é que **quanto mais você espera, mais sua condição pode piorar**. E aí o tratamento fica mais longo e mais caro.

Que tal agendar uma **avaliação gratuita** para você conhecer nossa estrutura e tirar todas as dúvidas? Sem compromisso! 

Assim você decide com mais segurança. O que acha?"""
    
    def _tratar_objecao_desconfianca(self, nome: str) -> str:
        """Trata objeção de desconfiança"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}entendo sua cautela! É super importante confiar em quem vai cuidar da sua saúde. 🏥

**SOBRE A FT9 INTELLIGENCE:**

✅ **+15 anos** de experiência
✅ **+10.000 pacientes** atendidos
✅ **Equipe especializada** com certificações internacionais
✅ **Tecnologia de ponta** em diagnóstico
✅ **4.9 estrelas** no Google (veja nossos depoimentos!)

**DIFERENCIAIS:**
→ Método PTC 2025 exclusivo
→ Acompanhamento via IA (AI9)
→ Resultados mensuráveis
→ Garantia de satisfação

**QUER VER PROVAS?**
Posso te mostrar:
→ Depoimentos em vídeo
→ Casos de sucesso
→ Nossas instalações
→ Certificações da equipe

O que te deixaria mais seguro(a) para dar esse passo?"""
    
    def _tratar_objecao_prioridade(self, nome: str) -> str:
        """Trata objeção de prioridade"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}entendo que você não sinta urgência agora. Mas deixa eu te contar algo importante: 🚨

**A DOR É UM SINAL DE ALERTA**

Quando você sente dor, seu corpo está te dizendo:
→ "Algo está errado"
→ "Preciso de ajuda"
→ "Não ignore isso"

**O QUE ACONTECE SE ESPERAR:**
❌ Compensações musculares
❌ Agravamento do quadro
❌ Dor crônica (mais difícil de tratar)
❌ Tratamento mais longo e caro
❌ Possível necessidade de cirurgia

**PREVENIR É MELHOR QUE REMEDIAR**

Nossa experiência mostra que:
→ Tratamento precoce = Recuperação 3x mais rápida
→ Prevenção = Economia de 70% em custos
→ Qualidade de vida = Sem preço

Que tal fazer uma **avaliação preventiva**? Assim você sabe exatamente o que está acontecendo e pode decidir com clareza.

Posso agendar para você?"""
    
    def _tratar_objecao_comparacao(self, nome: str) -> str:
        """Trata objeção de comparação"""
        saudacao = f"{nome}, " if nome else ""
        
        return f"""{saudacao}é super válido pesquisar e comparar! Isso mostra que você se importa com sua escolha. 🔍

**MAS ATENÇÃO AO COMPARAR:**

Não compare apenas preço. Compare:
✅ **Qualificação da equipe** (certificações, experiência)
✅ **Tecnologia utilizada** (equipamentos modernos)
✅ **Método de tratamento** (PTC 2025 é exclusivo)
✅ **Acompanhamento** (temos IA + humano)
✅ **Resultados** (taxa de sucesso comprovada)
✅ **Suporte** (WhatsApp 24/7 com AI9)

**COMPARAÇÃO JUSTA:**

🏥 **Clínica comum:**
→ Sessão avulsa: R$ 120-180
→ Sem acompanhamento contínuo
→ Sem tecnologia de IA
→ Atendimento básico

🌟 **FT9 Intelligence:**
→ PTC 2025: R$ 997/mês (ilimitado)
→ Acompanhamento 24/7
→ IA + Equipe especializada
→ Método exclusivo

**GARANTIA FT9:**
Se em 30 dias você não ver resultados, devolvemos seu investimento.

Quer agendar uma visita para conhecer nossa estrutura e decidir com segurança?"""
    
    def _tratar_objecao_geral(self, interpretacao: Dict, usuario: str) -> str:
        """Trata objeção genérica com GPT"""
        mensagem = interpretacao.get("mensagem_original", "")
        persona = interpretacao.get("persona", {})
        
        contexto = """Você é o AI9, especialista em tratamento de objeções da FT9 Intelligence.

TÉCNICA DE TRATAMENTO DE OBJEÇÕES:
1. **Empatia**: "Entendo sua preocupação..."
2. **Clarificação**: Fazer pergunta para entender melhor
3. **Resposta**: Apresentar solução ou perspectiva diferente
4. **Prova**: Dar evidências, casos de sucesso
5. **Ação**: Conduzir para próximo passo

Seja empático, consultivo e sempre conduza para avaliação ou agendamento.
Use técnicas de vendas consultivas."""
        
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
        
        # Se aceitou e quer fechar, vai para ClosingFlow
        if any(palavra in mensagem for palavra in ["ok", "vamos", "quero", "pode agendar", "fechado"]):
            return "closing_flow"
        
        # Se ainda tem dúvidas, volta para SalesFlow
        if any(palavra in mensagem for palavra in ["mas", "porém", "ainda", "dúvida"]):
            return "sales_flow"
        
        # Se mencionou urgência, vai para UrgencyFlow
        if any(palavra in mensagem for palavra in ["urgente", "rápido", "logo"]):
            return "urgency_flow"
        
        return None
