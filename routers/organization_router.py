"""
Rotas de gerenciamento de organizações
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import re
from database import get_db, Organization, User, UserRole
from auth import get_current_active_user, get_password_hash, require_role
from schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    UserResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])


def generate_slug(name: str) -> str:
    """Gerar slug a partir do nome"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Criar nova organização (com usuário admin)
    Endpoint público para onboarding
    """
    # Verificar se email da organização já existe
    result = await db.execute(
        select(Organization).where(Organization.email == org_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email da organização já cadastrado"
        )
    
    # Verificar se email do admin já existe
    result = await db.execute(
        select(User).where(User.email == org_data.admin_email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email do administrador já cadastrado"
        )
    
    # Gerar slug único
    base_slug = generate_slug(org_data.name)
    slug = base_slug
    counter = 1
    
    while True:
        result = await db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    try:
        # Criar organização
        slug = generate_slug(org_data.name)
        
        organization = Organization(
            name=org_data.name,
            slug=slug,
            email=org_data.email,
            phone=org_data.phone,
            address=org_data.address,
            city=org_data.city,
            state=org_data.state
        )
        
        db.add(organization)
        await db.flush()  # Para obter o ID
        
        # Criar usuário admin
        hashed_pwd = get_password_hash(org_data.admin_password)
        
        admin_user = User(
            organization_id=organization.id,
            email=org_data.admin_email,
            hashed_password=hashed_pwd,
            full_name=org_data.admin_full_name,
            role=UserRole.ORG_ADMIN,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(organization)
        
        logger.info(f"Organização criada: {organization.name} ({organization.slug})")
        
        return organization
        
    except Exception as e:
        logger.error(f"Erro ao criar organização: {type(e).__name__}: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar organização: {str(e)}"
        )


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter organização do usuário atual
    """
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organização não encontrada"
        )
    
    return organization


@router.patch("/me", response_model=OrganizationResponse)
async def update_my_organization(
    org_update: OrganizationUpdate,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualizar organização (apenas admin)
    """
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organização não encontrada"
        )
    
    # Atualizar campos
    update_data = org_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    await db.commit()
    await db.refresh(organization)
    
    logger.info(f"Organização atualizada: {organization.name}")
    
    return organization


@router.get("/me/users", response_model=List[UserResponse])
async def get_organization_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar usuários da organização
    """
    result = await db.execute(
        select(User).where(User.organization_id == current_user.organization_id)
    )
    users = result.scalars().all()
    
    return users
