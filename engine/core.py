"""
FT9 Core Engine - Núcleo de Processamento de Mensagens
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FT9Core:
    """
    Núcleo central do FT9 Intelligence
    Responsável por interpretar intenções e processar mensagens
    """
    
    def __init__(self, memory_engine, flow_manager):
        """
        Inicializa o núcleo FT9
        
        Args:
            memory_engine: Instância do FT9Memory
            flow_manager: Instância do FT9Flow
        """
        self.memory = memory_engine
        self.flow = flow_manager
        logger.info("FT9Core inicializado com sucesso")
    
    def interpretar(self, mensagem: str, usuario: str) -> Dict[str, Any]:
        """
        Interpreta a intenção do usuário baseado na mensagem
        
        Args:
            mensagem: Texto da mensagem do usuário
            usuario: Identificador do usuário (número de telefone)
            
        Returns:
            Dict com intenção identificada e metadados
        """
        msg = mensagem.lower().strip()
        
        # Detecção de intenções expandida
        interpretacao = {
            "intencao": "mensagem_livre",
            "usuario": usuario,
            "mensagem_original": mensagem,
            "keywords_detectadas": []
        }
        
        # Agendamento
        if any(kw in msg for kw in ["agendar", "marcar", "consulta", "horário", "agenda"]):
            interpretacao["intencao"] = "agendamento"
            interpretacao["keywords_detectadas"].append("agendamento")
            logger.info(f"Intenção detectada: agendamento para {usuario}")
        
        # PTC 2025 - Perguntas sobre o curso
        elif any(kw in msg for kw in ["ptc", "curso", "aula", "treinamento", "programa"]):
            interpretacao["intencao"] = "ptc_fluxo"
            interpretacao["keywords_detectadas"].append("ptc")
            
            # Detectar número de aula específica
            import re
            aula_match = re.search(r'aula\s*(\d+)', msg)
            if aula_match:
                interpretacao["aula_numero"] = int(aula_match.group(1))
                logger.info(f"Aula específica detectada: {interpretacao['aula_numero']}")
            
            logger.info(f"Intenção detectada: PTC para {usuario}")
        
        # Dúvidas gerais
        elif any(kw in msg for kw in ["duvida", "dúvida", "pergunta", "como", "o que", "qual", "?"]):
            interpretacao["intencao"] = "pergunta"
            interpretacao["keywords_detectadas"].append("pergunta")
            logger.info(f"Intenção detectada: pergunta para {usuario}")
        
        # Saudações
        elif any(kw in msg for kw in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey", "hello"]):
            interpretacao["intencao"] = "saudacao"
            interpretacao["keywords_detectadas"].append("saudacao")
            logger.info(f"Intenção detectada: saudação para {usuario}")
        
        # Ajuda
        elif any(kw in msg for kw in ["ajuda", "help", "comandos", "o que você faz"]):
            interpretacao["intencao"] = "ajuda"
            interpretacao["keywords_detectadas"].append("ajuda")
            logger.info(f"Intenção detectada: ajuda para {usuario}")
        
        else:
            logger.info(f"Intenção padrão: mensagem_livre para {usuario}")
        
        return interpretacao
    
    def processar(self, mensagem: str, usuario: str, contexto: Optional[Dict] = None) -> str:
        """
        Processa uma mensagem completa através do fluxo
        
        Args:
            mensagem: Texto da mensagem
            usuario: Identificador do usuário
            contexto: Contexto adicional (histórico, persona, etc)
            
        Returns:
            Resposta processada para o usuário
        """
        try:
            # Interpreta a intenção
            interpretacao = self.interpretar(mensagem, usuario)
            
            # Adiciona contexto se disponível
            if contexto:
                interpretacao["contexto"] = contexto
            
            # Carrega persona do usuário se existir
            persona = self.memory.get_persona(usuario)
            if persona:
                interpretacao["persona"] = persona
                logger.info(f"Persona carregada para {usuario}")
            
            # Executa o fluxo apropriado
            resposta = self.flow.executar_fluxo(interpretacao, usuario)
            
            logger.info(f"Mensagem processada com sucesso para {usuario}")
            return resposta
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de {usuario}: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status do núcleo FT9
        
        Returns:
            Dict com informações de status
        """
        return {
            "status": "online",
            "memory_loaded": self.memory is not None,
            "flow_loaded": self.flow is not None,
            "personas_count": len(self.memory.personas) if self.memory else 0
        }
