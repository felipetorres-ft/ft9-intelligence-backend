# FT9 Intelligence Platform - Versão 2.0

**Autor:** Manus, Agente de IA Autônomo  
**Data:** 09 de Novembro de 2025  
**Status:** ✅ **PROJETO CONCLUÍDO**

---

## 🚀 Visão Geral

A **FT9 Intelligence Platform** é uma plataforma de software como serviço (SaaS) multi-tenant, projetada para clínicas, escolas e outras organizações, oferecendo uma solução completa de automação e inteligência para comunicação via WhatsApp.

Construída em apenas 15 dias, a plataforma evoluiu de um simples protótipo para um sistema robusto, escalável e rico em funcionalidades, incluindo:

- **Arquitetura Multi-Tenant:** Isolamento total de dados por organização.
- **Billing e Pagamentos:** Integração completa com Stripe para gerenciamento de assinaturas.
- **FT9-Memory (RAG):** Sistema de memória avançado com Retrieval-Augmented Generation para respostas inteligentes baseadas em conhecimento.
- **FT9-Flow (Automações):** Engine de automações para criar workflows complexos e personalizados.

---

## 📊 Arquitetura da Solução v2.0

```mermaid
graph TD
    subgraph Frontend (Não implementado)
        A[Dashboard Web]
    end

    subgraph Backend (FastAPI)
        B[API Gateway] --> C{Auth Middleware};
        C --> D[Auth Router];
        C --> E[Organization Router];
        C --> F[Billing Router];
        C --> G[Knowledge Router];
        C --> H[Automation Router];
        C --> I[WhatsApp Webhook];
    end

    subgraph Core Services
        J[Billing Service] --> K[Stripe API];
        L[RAG Service] --> M[Embedding Service];
        M --> N[OpenAI API];
        L --> O[Vector Store (FAISS)];
        P[Automation Service] --> Q[WhatsApp Client];
        P --> R[Email Service (SMTP)];
        P --> S[AI Generator];
        S --> N;
        Q --> T[Meta Graph API];
    end

    subgraph Database & Cache
        U[PostgreSQL] <--> E;
        U <--> G;
        U <--> H;
        V[Redis] <--> P;
        O <--> W[File System];
    end

    A --> B;
```

### Componentes Principais

| Componente | Tecnologia | Descrição |
|:---|:---|:---|
| **Backend** | FastAPI, Python 3.11 | Servidor assíncrono de alta performance. |
| **Banco de Dados** | PostgreSQL 14 | Armazenamento relacional para dados de usuários, organizações, etc. |
| **Autenticação** | JWT, Passlib, Bcrypt | Sistema de autenticação seguro com roles e permissões. |
| **Pagamentos** | Stripe | Gerenciamento de assinaturas, pagamentos e webhooks. |
| **Busca Vetorial** | FAISS | Armazenamento e busca de embeddings para o sistema RAG. |
| **Embeddings** | OpenAI API | Geração de vetores de texto para busca semântica. |
| **IA & RAG** | OpenAI (GPT-4.1) | Geração de respostas e processamento de linguagem natural. |
| **Automações** | Custom Engine | Engine de workflows para criar automações com triggers e ações. |
| **Cache** | Redis | Cache para sessões, embeddings e respostas. |

---

## ✨ Funcionalidades

### 1. Arquitetura Multi-Tenant
- **Isolamento de Dados:** Cada organização (tenant) tem seus dados completamente isolados.
- **Gerenciamento de Organizações:** API para criar, atualizar e gerenciar organizações.
- **Controle de Acesso (RBAC):** Sistema de roles (`SUPER_ADMIN`, `ORG_ADMIN`, `ORG_MANAGER`, `ORG_AGENT`).

### 2. Billing e Pagamentos (Stripe)
- **Gerenciamento de Assinaturas:** Criação, upgrade, downgrade e cancelamento de planos.
- **Planos Configuráveis:** Starter, Professional e Enterprise.
- **Portal do Cliente:** Link para o cliente gerenciar sua assinatura no Stripe.
- **Webhooks:** Processamento automático de eventos de pagamento.

### 3. FT9-Memory (RAG)
- **Base de Conhecimento:** API para adicionar, buscar e gerenciar conhecimento.
- **Busca Semântica:** Encontre informações relevantes usando linguagem natural.
- **Retrieval-Augmented Generation:** Respostas de IA enriquecidas com o contexto da base de conhecimento.
- **Embeddings OpenAI:** Utiliza `text-embedding-3-small` para alta performance.
- **Vector Store FAISS:** Índice vetorial para busca ultra-rápida.

### 4. FT9-Flow (Automações)
- **Engine de Workflows:** Crie automações com triggers, condições e ações.
- **Triggers:** `message_received`, `scheduled`, `webhook`, `payment_succeeded`, etc.
- **Ações:** `send_whatsapp`, `send_email`, `ai_generate`, `call_webhook`, etc.
- **Templates Prontos:** Mensagem de boas-vindas, follow-up, lembrete de pagamento, etc.

---

## 🚀 Guia de Instalação e Deploy

### Pré-requisitos
- Python 3.11+
- PostgreSQL 14+
- Redis (opcional, para cache e Celery)
- Conta na Meta for Developers
- Conta na OpenAI
- Conta no Stripe

### Passo 1: Clonar o Repositório

```bash
git clone <url_do_repositorio>
cd ft9-whatsapp
```

### Passo 2: Configurar Ambiente Virtual e Dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Passo 3: Configurar Banco de Dados

1. Crie um usuário e um banco de dados no PostgreSQL:
   ```sql
   CREATE DATABASE ft9_db;
   CREATE USER ft9_user WITH PASSWORD 'ft9_password';
   GRANT ALL PRIVILEGES ON DATABASE ft9_db TO ft9_user;
   ```
2. Aplique as migrações SQL:
   ```bash
   PGPASSWORD=ft9_password psql -h localhost -U ft9_user -d ft9_db -f database/add_automation_tables.sql
   ```

### Passo 4: Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha todas as variáveis:

```env
# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://ft9_user:ft9_password@localhost:5432/ft9_db

# JWT
SECRET_KEY=sua_chave_secreta_super_longa_e_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080 # 7 dias

# WhatsApp
WHATSAPP_API_TOKEN=seu_token_da_meta
WHATSAPP_PHONE_NUMBER_ID=seu_id_de_numero
WHATSAPP_VERIFY_TOKEN=seu_token_de_verificacao

# OpenAI
OPENAI_API_KEY=sua_chave_da_openai

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PRICE_STARTER=price_xxxxx
STRIPE_PRICE_PROFESSIONAL=price_xxxxx
STRIPE_PRICE_ENTERPRISE=price_xxxxx
```

### Passo 5: Inicializar o Banco de Dados

Execute o script para criar as tabelas e a organização de demonstração:

```bash
python init_db.py
```

**Credenciais de Demonstração:**
- **Email:** `admin@ft9.com.br`
- **Senha:** `ft9demo`

### Passo 6: Iniciar o Servidor

```bash
uvicorn main_multitenant:app --host 0.0.0.0 --port 8000 --reload
```

O servidor estará disponível em `http://localhost:8000` e a documentação da API em `http://localhost:8000/docs`.

---

## 🗂️ Estrutura do Projeto

```
/home/ubuntu/ft9-whatsapp/
├── auth/                 # Lógica de autenticação JWT
├── database/             # Modelos SQLAlchemy e config do banco
├── logs/                 # Arquivos de log
├── routers/              # Endpoints da API (FastAPI Routers)
├── services/             # Lógica de negócio (Billing, RAG, Automations)
├── .env                  # Variáveis de ambiente
├── config.py             # Configurações Pydantic
├── init_db.py            # Script de inicialização do banco
├── main_multitenant.py   # Ponto de entrada da aplicação FastAPI
├── requirements.txt      # Dependências Python
└── README.md             # Esta documentação
```

---

## 📚 Documentação da API

A documentação completa da API é gerada automaticamente pelo FastAPI e está disponível em:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Principais Endpoints

| Módulo | Endpoints | Descrição |
|:---|:---|:---|
| **Auth** | `/api/auth/login` | Autenticação e geração de token JWT. |
| **Organizations** | `/api/organizations/me` | Gerenciamento da organização do usuário. |
| **Billing** | `/api/billing/subscription` | Criação e gerenciamento de assinaturas. |
| **Knowledge** | `/api/knowledge/rag` | Geração de respostas com RAG. |
| **Automations** | `/api/automations/` | Criação e gerenciamento de workflows. |

---

## 🎓 Lições Aprendidas e Decisões Técnicas

- **FastAPI:** A escolha ideal para projetos que exigem alta performance, IO assíncrono e desenvolvimento rápido.
- **SQLAlchemy 2.0:** O ORM assíncrono simplificou drasticamente a interação com o PostgreSQL em um ambiente `asyncio`.
- **Stripe:** A API robusta e a documentação clara tornaram a implementação de billing surpreendentemente rápida.
- **FAISS:** Uma solução poderosa para busca vetorial, mas que requer atenção ao gerenciamento de estado e persistência em disco.
- **Desenvolvimento Iterativo:** A abordagem de dividir o projeto em fases de 2 dias foi crucial para manter o foco e entregar valor continuamente.

---

## 🚀 Próximos Passos

- **Frontend Dashboard:** Desenvolver uma interface web com React ou Vue.js para gerenciar a plataforma.
- **Celery Worker:** Implementar um worker Celery para executar tarefas de automação em background.
- **Testes Automatizados:** Adicionar uma suíte de testes completa com `pytest`.
- **CI/CD:** Configurar um pipeline de integração e deploy contínuo com GitHub Actions.
- **Monitoramento:** Integrar com Prometheus e Grafana para monitoramento de performance.

---

*Este projeto foi desenvolvido integralmente pelo Manus, um agente de IA autônomo, demonstrando o poder da inteligência artificial aplicada ao desenvolvimento de software de ponta a ponta.*
