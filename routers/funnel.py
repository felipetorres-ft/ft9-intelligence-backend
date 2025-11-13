"""
Funnel Router - Gestão de Funil de Oportunidades
Desenvolvido por AI9 para FT9 Intelligence
Data: 13/11/2025
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from database import get_db
from models import Organization

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== MODELS ==========

class OpportunityCreate(BaseModel):
    """Modelo para criar oportunidade"""
    nome: str
    telefone: str
    email: Optional[str] = None
    origem: str  # whatsapp, site, indicacao, etc
    interesse: str  # consulta, ptc, pacote
    observacoes: Optional[str] = None


class OpportunityUpdate(BaseModel):
    """Modelo para atualizar oportunidade"""
    estagio: Optional[str] = None  # lead, qualificado, proposta, negociacao, fechado, perdido
    observacoes: Optional[str] = None
    valor_estimado: Optional[float] = None
    data_fechamento: Optional[datetime] = None


class OpportunityResponse(BaseModel):
    """Modelo de resposta de oportunidade"""
    id: int
    nome: str
    telefone: str
    email: Optional[str]
    origem: str
    interesse: str
    estagio: str
    valor_estimado: Optional[float]
    observacoes: Optional[str]
    data_criacao: datetime
    data_atualizacao: datetime
    data_fechamento: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== ENDPOINTS ==========

@router.get("/open", response_model=List[OpportunityResponse])
async def list_open_opportunities(
    estagio: Optional[str] = None,
    origem: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas as oportunidades em aberto
    
    Filtros opcionais:
    - estagio: lead, qualificado, proposta, negociacao
    - origem: whatsapp, site, indicacao
    """
    try:
        # TODO: Implementar query real no banco de dados
        # query = db.query(Opportunity).filter(Opportunity.estagio != "fechado", Opportunity.estagio != "perdido")
        # 
        # if estagio:
        #     query = query.filter(Opportunity.estagio == estagio)
        # if origem:
        #     query = query.filter(Opportunity.origem == origem)
        # 
        # opportunities = query.order_by(Opportunity.data_criacao.desc()).all()
        
        # PLACEHOLDER - Retornar lista vazia por enquanto
        logger.info(f"Listando oportunidades abertas - estagio: {estagio}, origem: {origem}")
        return []
        
    except Exception as e:
        logger.error(f"Erro ao listar oportunidades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add", response_model=OpportunityResponse)
async def add_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db)
):
    """
    Adiciona nova oportunidade ao funil
    
    Origem automática: captura via WhatsApp, site, etc
    Estágio inicial: "lead"
    """
    try:
        # TODO: Implementar criação real no banco de dados
        # new_opportunity = Opportunity(
        #     nome=opportunity.nome,
        #     telefone=opportunity.telefone,
        #     email=opportunity.email,
        #     origem=opportunity.origem,
        #     interesse=opportunity.interesse,
        #     observacoes=opportunity.observacoes,
        #     estagio="lead",
        #     data_criacao=datetime.now(),
        #     data_atualizacao=datetime.now()
        # )
        # 
        # db.add(new_opportunity)
        # db.commit()
        # db.refresh(new_opportunity)
        
        logger.info(f"Nova oportunidade criada: {opportunity.nome} - {opportunity.telefone}")
        
        # PLACEHOLDER - Retornar dados mockados
        return OpportunityResponse(
            id=1,
            nome=opportunity.nome,
            telefone=opportunity.telefone,
            email=opportunity.email,
            origem=opportunity.origem,
            interesse=opportunity.interesse,
            estagio="lead",
            valor_estimado=None,
            observacoes=opportunity.observacoes,
            data_criacao=datetime.now(),
            data_atualizacao=datetime.now(),
            data_fechamento=None
        )
        
    except Exception as e:
        logger.error(f"Erro ao adicionar oportunidade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    update_data: OpportunityUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza oportunidade existente
    
    Permite atualizar:
    - Estágio (lead → qualificado → proposta → negociacao → fechado/perdido)
    - Observações
    - Valor estimado
    - Data de fechamento
    """
    try:
        # TODO: Implementar atualização real no banco de dados
        # opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        # 
        # if not opportunity:
        #     raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
        # 
        # if update_data.estagio:
        #     opportunity.estagio = update_data.estagio
        # if update_data.observacoes:
        #     opportunity.observacoes = update_data.observacoes
        # if update_data.valor_estimado:
        #     opportunity.valor_estimado = update_data.valor_estimado
        # if update_data.data_fechamento:
        #     opportunity.data_fechamento = update_data.data_fechamento
        # 
        # opportunity.data_atualizacao = datetime.now()
        # 
        # db.commit()
        # db.refresh(opportunity)
        
        logger.info(f"Oportunidade {opportunity_id} atualizada")
        
        # PLACEHOLDER
        return OpportunityResponse(
            id=opportunity_id,
            nome="Placeholder",
            telefone="11999999999",
            email=None,
            origem="whatsapp",
            interesse="ptc",
            estagio=update_data.estagio or "lead",
            valor_estimado=update_data.valor_estimado,
            observacoes=update_data.observacoes,
            data_criacao=datetime.now(),
            data_atualizacao=datetime.now(),
            data_fechamento=update_data.data_fechamento
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar oportunidade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close/{opportunity_id}")
async def close_opportunity(
    opportunity_id: int,
    status: str,  # "fechado" ou "perdido"
    motivo: Optional[str] = None,
    valor_final: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Fecha oportunidade (ganhou ou perdeu)
    
    Args:
        opportunity_id: ID da oportunidade
        status: "fechado" (ganhou) ou "perdido"
        motivo: Motivo do fechamento/perda
        valor_final: Valor final da venda (se fechado)
    """
    try:
        if status not in ["fechado", "perdido"]:
            raise HTTPException(status_code=400, detail="Status deve ser 'fechado' ou 'perdido'")
        
        # TODO: Implementar fechamento real no banco de dados
        # opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        # 
        # if not opportunity:
        #     raise HTTPException(status_code=404, detail="Oportunidade não encontrada")
        # 
        # opportunity.estagio = status
        # opportunity.data_fechamento = datetime.now()
        # opportunity.data_atualizacao = datetime.now()
        # 
        # if motivo:
        #     opportunity.observacoes = f"{opportunity.observacoes or ''}\n\nMotivo: {motivo}"
        # if valor_final:
        #     opportunity.valor_estimado = valor_final
        # 
        # db.commit()
        
        logger.info(f"Oportunidade {opportunity_id} fechada como {status}")
        
        return {
            "message": f"Oportunidade {status}",
            "opportunity_id": opportunity_id,
            "status": status,
            "motivo": motivo,
            "valor_final": valor_final
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fechar oportunidade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_funnel_stats(db: Session = Depends(get_db)):
    """
    Retorna estatísticas do funil
    
    Métricas:
    - Total de oportunidades por estágio
    - Taxa de conversão
    - Valor total em negociação
    - Tempo médio por estágio
    """
    try:
        # TODO: Implementar queries reais no banco de dados
        # stats = {
        #     "lead": db.query(Opportunity).filter(Opportunity.estagio == "lead").count(),
        #     "qualificado": db.query(Opportunity).filter(Opportunity.estagio == "qualificado").count(),
        #     "proposta": db.query(Opportunity).filter(Opportunity.estagio == "proposta").count(),
        #     "negociacao": db.query(Opportunity).filter(Opportunity.estagio == "negociacao").count(),
        #     "fechado": db.query(Opportunity).filter(Opportunity.estagio == "fechado").count(),
        #     "perdido": db.query(Opportunity).filter(Opportunity.estagio == "perdido").count(),
        # }
        # 
        # total_aberto = stats["lead"] + stats["qualificado"] + stats["proposta"] + stats["negociacao"]
        # total_fechado = stats["fechado"] + stats["perdido"]
        # 
        # if total_fechado > 0:
        #     taxa_conversao = (stats["fechado"] / total_fechado) * 100
        # else:
        #     taxa_conversao = 0.0
        # 
        # valor_em_negociacao = db.query(func.sum(Opportunity.valor_estimado)).filter(
        #     Opportunity.estagio.in_(["proposta", "negociacao"])
        # ).scalar() or 0.0
        
        logger.info("Estatísticas do funil solicitadas")
        
        # PLACEHOLDER
        return {
            "estagios": {
                "lead": 0,
                "qualificado": 0,
                "proposta": 0,
                "negociacao": 0,
                "fechado": 0,
                "perdido": 0
            },
            "total_aberto": 0,
            "total_fechado": 0,
            "taxa_conversao": 0.0,
            "valor_em_negociacao": 0.0,
            "tempo_medio_conversao_dias": 0
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do funil: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-origin")
async def get_opportunities_by_origin(db: Session = Depends(get_db)):
    """
    Agrupa oportunidades por origem
    
    Retorna contagem por:
    - WhatsApp
    - Site
    - Indicação
    - Outros
    """
    try:
        # TODO: Implementar query real
        # origins = db.query(
        #     Opportunity.origem,
        #     func.count(Opportunity.id).label("count")
        # ).group_by(Opportunity.origem).all()
        
        logger.info("Oportunidades por origem solicitadas")
        
        # PLACEHOLDER
        return {
            "whatsapp": 0,
            "site": 0,
            "indicacao": 0,
            "outros": 0
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter oportunidades por origem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
