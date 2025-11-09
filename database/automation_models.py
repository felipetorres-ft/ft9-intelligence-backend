"""
Modelos de banco de dados para FT9-Flow (Automações)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.models import Base


class Automation(Base):
    """
    Automação/Workflow
    """
    __tablename__ = "automations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Trigger
    trigger_type = Column(String(50), nullable=False)  # message_received, scheduled, webhook, etc.
    trigger_config = Column(JSON)  # Configuração específica do trigger
    
    # Condições
    conditions = Column(JSON)  # Lista de condições (if/else)
    
    # Ações
    actions = Column(JSON, nullable=False)  # Lista de ações a executar
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True))
    execution_count = Column(Integer, default=0)
    
    # Relacionamentos
    executions = relationship("AutomationExecution", back_populates="automation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Automation {self.name} (Org: {self.organization_id})>"


class AutomationExecution(Base):
    """
    Execução de uma automação
    """
    __tablename__ = "automation_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False, index=True)
    
    # Status
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    
    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    automation = relationship("Automation", back_populates="executions")
    
    def __repr__(self):
        return f"<AutomationExecution {self.id} (Status: {self.status})>"


class ScheduledTask(Base):
    """
    Tarefa agendada
    """
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    
    # Agendamento
    schedule_type = Column(String(20), nullable=False)  # once, daily, weekly, monthly, cron
    schedule_config = Column(JSON, nullable=False)  # Configuração do agendamento
    
    # Próxima execução
    next_run_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_run_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<ScheduledTask {self.id} (Next: {self.next_run_at})>"
