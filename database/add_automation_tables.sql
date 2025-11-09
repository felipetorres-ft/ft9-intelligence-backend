-- Adicionar tabelas de automação

CREATE TABLE IF NOT EXISTS automations (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_config JSONB,
    conditions JSONB,
    actions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0
);

CREATE INDEX idx_automations_org ON automations(organization_id);
CREATE INDEX idx_automations_trigger ON automations(trigger_type);

CREATE TABLE IF NOT EXISTS automation_executions (
    id SERIAL PRIMARY KEY,
    automation_id INTEGER NOT NULL REFERENCES automations(id),
    status VARCHAR(20) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_automation_executions_automation ON automation_executions(automation_id);
CREATE INDEX idx_automation_executions_status ON automation_executions(status);

CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    automation_id INTEGER NOT NULL REFERENCES automations(id),
    schedule_type VARCHAR(20) NOT NULL,
    schedule_config JSONB NOT NULL,
    next_run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_run_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_scheduled_tasks_org ON scheduled_tasks(organization_id);
CREATE INDEX idx_scheduled_tasks_next_run ON scheduled_tasks(next_run_at);
