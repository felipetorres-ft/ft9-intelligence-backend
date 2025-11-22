"""
Mini Cinthya Chat Router
Implementado conforme arquitetura da AI9
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os
from pathlib import Path

router = APIRouter(prefix="/mini-cinthya", tags=["Mini Cinthya"])

# Modelos de dados
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str

# Carregar persona completa
def load_persona() -> str:
    """Carrega e concatena todos os arquivos de persona da Mini Cinthya"""
    persona_dir = Path(__file__).parent.parent / "personas" / "mini-cinthya"
    
    files = [
        "persona_mestre_mini_cinthya.md",
        "mini_cinthya_captadora.md",
        "filosofia_cinthya.md",
        "slogan_oficial.txt",
        "formacoes_e_especialidades.md",
        "abordagem_regenerativa.md"
    ]
    
    persona_parts = []
    for filename in files:
        file_path = persona_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                persona_parts.append(f.read())
        else:
            raise FileNotFoundError(f"Arquivo de persona não encontrado: {filename}")
    
    return "\n\n".join(persona_parts)

# Carregar persona uma vez no início
PERSONA = load_persona()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint de chat com a Mini Cinthya
    Recebe mensagem e histórico, retorna resposta via OpenAI API
    """
    try:
        # Importar OpenAI
        from openai import OpenAI
        
        # Criar cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")
        
        client = OpenAI(api_key=api_key)
        
        # Preparar mensagens
        messages = [
            {"role": "system", "content": PERSONA}
        ]
        
        # Adicionar histórico
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": request.message})
        
        # Chamar OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.5
        )
        
        # Extrair resposta
        response_content = completion.choices[0].message.content
        
        return ChatResponse(response=response_content)
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar persona: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar chat: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check do serviço Mini Cinthya"""
    return {
        "status": "ok",
        "service": "Mini Cinthya Chat",
        "persona_loaded": len(PERSONA) > 0
    }
