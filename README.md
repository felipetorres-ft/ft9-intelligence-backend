# FT9 Intelligence Platform - Backend API

Sistema SaaS Multi-Tenant para WhatsApp Business com IA, RAG e Automações.

## 🚀 Deploy no Railway

### 1. Conectar Repositório
- No Railway, click em "+ Create" → "GitHub Repo"
- Selecione este repositório

### 2. Configurar Variáveis de Ambiente
Adicione em Settings → Variables:

```
SECRET_KEY=ft9_super_secret_key_production_2025_very_long_and_secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
OPENAI_API_KEY=sua_chave_aqui
```

### 3. Conectar PostgreSQL
- O Railway detectará automaticamente a DATABASE_URL do PostgreSQL no mesmo projeto

### 4. Deploy Automático
- Railway fará build e deploy automaticamente usando o Dockerfile

## 📚 Documentação da API

Após o deploy, acesse:
- Swagger UI: `https://seu-dominio.railway.app/docs`
- ReDoc: `https://seu-dominio.railway.app/redoc`

## 🔐 Credenciais Demo

```
Email: admin@ft9.com.br
Senha: ft9demo
```

## 🛠️ Stack Tecnológica

- FastAPI (Python 3.11)
- PostgreSQL
- OpenAI GPT-4
- FAISS (Vector Store)
- Stripe (Billing)
- JWT Authentication

---

Desenvolvido com ❤️ pela equipe FT9
