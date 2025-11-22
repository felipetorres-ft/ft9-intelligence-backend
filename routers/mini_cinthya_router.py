"""
Mini Cinthya Chat Router
Implementado conforme patch oficial da AI9
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
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

@router.post("/chat", response_model=ChatResponse)
async def mini_cinthya_chat(payload: ChatRequest):
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
        
        # Carregar persona
        persona_path = Path("/app/kdb/cinthya/persona_mestre_mini_cinthya.md")
        if not persona_path.exists():
            # Fallback para ambiente local
            persona_path = Path(__file__).parent.parent / "kdb" / "cinthya" / "persona_mestre_mini_cinthya.md"
        
        if not persona_path.exists():
            raise HTTPException(status_code=500, detail="Arquivo de persona não encontrado")
        
        with open(persona_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # Preparar mensagens
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Adicionar histórico
        for msg in payload.history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": payload.message})
        
        # Chamar OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o",
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
    persona_path = Path("/app/kdb/cinthya/persona_mestre_mini_cinthya.md")
    if not persona_path.exists():
        persona_path = Path(__file__).parent.parent / "kdb" / "cinthya" / "persona_mestre_mini_cinthya.md"
    
    return {
        "status": "ok",
        "service": "Mini Cinthya Chat",
        "persona_exists": persona_path.exists()
    }
