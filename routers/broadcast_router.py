"""
FT9 Intelligence - Broadcast Router
Endpoints para disparo massivo via Z-API
"""

from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.broadcast_service import process_csv_and_broadcast
from schemas.broadcast_schema import BroadcastResponse
from database import get_db, User
from auth import get_current_active_user

router = APIRouter(prefix="/broadcast", tags=["Broadcast"])


@router.post("/send", response_model=BroadcastResponse)
async def send_broadcast(
    csv_file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Inicia disparo massivo via upload de CSV
    
    **Autenticação:** Requerida (JWT)
    
    **Permissões:** org_admin
    
    **CSV Format:**
    ```csv
    nome,numero,clinica
    João Silva,5511999999999,Clínica ABC
    Maria Santos,5511988888888,Clínica XYZ
    ```
    
    **Campos:**
    - `nome`: Nome do contato (obrigatório)
    - `numero`: Número WhatsApp com DDI+DDD (obrigatório)
    - `clinica`: Nome da clínica (opcional, padrão: "FT9")
    
    **Limites:**
    - Máximo 500 mensagens/dia (anti-banimento)
    - Lotes de 50 mensagens
    - Intervalo de 8 segundos entre lotes
    
    **Processamento:**
    - Executa em background (não bloqueia API)
    - Logs detalhados de progresso
    - Relatório final ao concluir
    """
    # Validar permissão
    if current_user.role != "org_admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem enviar broadcasts"
        )
    
    # Validar arquivo CSV
    if not csv_file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Envie um arquivo CSV válido (.csv)"
        )
    
    # Ler conteúdo do CSV antes de adicionar ao background
    # (FastAPI fecha o arquivo após retornar a resposta)
    csv_content = await csv_file.read()
    
    # Adicionar tarefa em background com o conteúdo já lido
    background_tasks.add_task(process_csv_and_broadcast, csv_content)
    
    return BroadcastResponse(
        message="Broadcast iniciado com sucesso! O processamento está em andamento."
    )


@router.get("/status")
async def get_broadcast_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém status de broadcasts em andamento
    
    **Autenticação:** Requerida (JWT)
    
    TODO:
    - Implementar tracking de status em tempo real
    - Armazenar histórico de broadcasts no banco
    - Retornar estatísticas detalhadas
    """
    # TODO: Implementar tracking real
    return {
        "message": "Endpoint em desenvolvimento",
        "status": "not_implemented"
    }
