from pydantic import BaseModel
from datetime import datetime

class KnowledgeCreate(BaseModel):
    title: str
    category: str | None = None
    content: str

class KnowledgeOut(BaseModel):
    id: int
    title: str
    category: str | None
    content: str
    created_at: datetime
    
    class Config:
        orm_mode = True
