"""
FT9 Memory Engine - Sistema de Memória Permanente
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FT9Memory:
    """
    Sistema de memória permanente do FT9 Intelligence
    Gerencia personas, relacionamentos e contexto
    """
    
    def __init__(self, base_path="memory"):
        """
        Inicializa o sistema de memória
        
        Args:
            base_path: Caminho base para arquivos de memória
        """
        self.base = base_path
        self._ensure_directories()
        
        # Carregar dados
        self.core = self._load_json("core.json")
        self.personas = self._load_dir("personas")
        self.relationships = self._load_dir("relationships")
        
        logger.info(f"FT9Memory inicializado: {len(self.personas)} personas carregadas")
    
    def _ensure_directories(self):
        """Garante que os diretórios necessários existem"""
        os.makedirs(self.base, exist_ok=True)
        os.makedirs(os.path.join(self.base, "personas"), exist_ok=True)
        os.makedirs(os.path.join(self.base, "relationships"), exist_ok=True)
    
    def _load_json(self, filename: str) -> Dict:
        """
        Carrega um arquivo JSON
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Dict com dados ou dict vazio
        """
        fp = os.path.join(self.base, filename)
        if os.path.exists(fp):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar {filename}: {str(e)}")
                return {}
        return {}
    
    def _load_dir(self, folder: str) -> Dict:
        """
        Carrega todos os JSONs de uma pasta
        
        Args:
            folder: Nome da pasta
            
        Returns:
            Dict com dados de todos os arquivos
        """
        p = os.path.join(self.base, folder)
        data = {}
        
        if not os.path.exists(p):
            return data
        
        for f in os.listdir(p):
            if f.endswith(".json"):
                try:
                    file_path = os.path.join(p, f)
                    with open(file_path, "r", encoding="utf-8") as file:
                        key = f.replace(".json", "")
                        data[key] = json.load(file)
                        logger.debug(f"Carregado: {folder}/{f}")
                except Exception as e:
                    logger.error(f"Erro ao carregar {folder}/{f}: {str(e)}")
        
        return data
    
    def _save_json(self, filename: str, data: Dict) -> bool:
        """
        Salva dados em arquivo JSON
        
        Args:
            filename: Nome do arquivo
            data: Dados para salvar
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            fp = os.path.join(self.base, filename)
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Arquivo salvo: {filename}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar {filename}: {str(e)}")
            return False
    
    def get_persona(self, usuario_id: str) -> Optional[Dict]:
        """
        Recupera persona de um usuário
        
        Args:
            usuario_id: Identificador do usuário (telefone)
            
        Returns:
            Dict com dados da persona ou None
        """
        # Normalizar ID (remover caracteres especiais)
        normalized_id = usuario_id.replace("+", "").replace("-", "").replace(" ", "")
        
        # Buscar por ID normalizado
        if normalized_id in self.personas:
            logger.info(f"Persona encontrada para {usuario_id}")
            return self.personas[normalized_id]
        
        # Buscar por ID original
        if usuario_id in self.personas:
            logger.info(f"Persona encontrada para {usuario_id}")
            return self.personas[usuario_id]
        
        logger.debug(f"Persona não encontrada para {usuario_id}")
        return None
    
    def save_persona(self, usuario_id: str, persona_data: Dict) -> bool:
        """
        Salva ou atualiza persona de um usuário
        
        Args:
            usuario_id: Identificador do usuário
            persona_data: Dados da persona
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Normalizar ID
            normalized_id = usuario_id.replace("+", "").replace("-", "").replace(" ", "")
            
            # Salvar em memória
            self.personas[normalized_id] = persona_data
            
            # Salvar em arquivo
            filename = os.path.join("personas", f"{normalized_id}.json")
            fp = os.path.join(self.base, "personas", f"{normalized_id}.json")
            
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(persona_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Persona salva para {usuario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar persona de {usuario_id}: {str(e)}")
            return False
    
    def update_persona(self, usuario_id: str, updates: Dict) -> bool:
        """
        Atualiza campos específicos de uma persona
        
        Args:
            usuario_id: Identificador do usuário
            updates: Dict com campos a atualizar
            
        Returns:
            True se sucesso, False se erro
        """
        persona = self.get_persona(usuario_id)
        
        if not persona:
            # Criar nova persona se não existir
            persona = {
                "identificacao": {},
                "fatos_confirmados": {},
                "perfil_psicologico": {},
                "relacao_com_FT": {},
                "AI9_modulacao": {},
                "memory_embeddings": {}
            }
        
        # Atualizar campos
        for key, value in updates.items():
            if key in persona:
                if isinstance(persona[key], dict) and isinstance(value, dict):
                    persona[key].update(value)
                else:
                    persona[key] = value
        
        # Salvar
        return self.save_persona(usuario_id, persona)
    
    def get_relationship(self, usuario_id: str) -> Optional[Dict]:
        """
        Recupera dados de relacionamento de um usuário
        
        Args:
            usuario_id: Identificador do usuário
            
        Returns:
            Dict com dados de relacionamento ou None
        """
        normalized_id = usuario_id.replace("+", "").replace("-", "").replace(" ", "")
        
        if normalized_id in self.relationships:
            return self.relationships[normalized_id]
        
        if usuario_id in self.relationships:
            return self.relationships[usuario_id]
        
        return None
    
    def list_personas(self) -> Dict[str, Dict]:
        """
        Lista todas as personas carregadas
        
        Returns:
            Dict com todas as personas
        """
        return self.personas
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da memória
        
        Returns:
            Dict com estatísticas
        """
        return {
            "personas_count": len(self.personas),
            "relationships_count": len(self.relationships),
            "core_loaded": bool(self.core),
            "base_path": self.base
        }
