"""
Endpoint temporário para atualizar organization com dados do WhatsApp
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database.database import get_db
from typing import Dict

router = APIRouter()

@router.post("/api/temp/update-whatsapp-org")
async def update_whatsapp_organization() -> Dict:
    """
    Endpoint temporário para atualizar a organization com os dados do WhatsApp
    """
    try:
        # Dados do WhatsApp
        PHONE_NUMBER_ID = "839615479241121"
        WABA_ID = "1505215831318900"
        PHONE_NUMBER = "+1 555 166 7990"
        ORG_ID = 19
        
        async for db in get_db():
            # Atualizar a organization
            query = text("""
                UPDATE organizations 
                SET whatsapp_phone_number_id = :phone_id,
                    whatsapp_business_account_id = :waba_id,
                    whatsapp_phone_number = :phone_number,
                    updated_at = NOW()
                WHERE id = :org_id
                RETURNING id, name, whatsapp_phone_number_id, whatsapp_business_account_id;
            """)
            
            result = await db.execute(
                query,
                {
                    "phone_id": PHONE_NUMBER_ID,
                    "waba_id": WABA_ID,
                    "phone_number": PHONE_NUMBER,
                    "org_id": ORG_ID
                }
            )
            
            await db.commit()
            row = result.fetchone()
            
            if row:
                return {
                    "success": True,
                    "message": "Organization atualizada com sucesso!",
                    "data": {
                        "id": row[0],
                        "name": row[1],
                        "whatsapp_phone_number_id": row[2],
                        "whatsapp_business_account_id": row[3]
                    }
                }
            else:
                raise HTTPException(status_code=404, detail="Organization não encontrada")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar organization: {str(e)}")
