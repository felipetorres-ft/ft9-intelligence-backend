# 🚀 FT9 Intelligence Backend

Backend da plataforma FT9 Intelligence - Sistema de gestão de organizações com autenticação segura.

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-green.svg)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)]()
[![Argon2](https://img.shields.io/badge/Argon2-23.1.0-orange.svg)]()

**Status:** ✅ **FUNCIONANDO PERFEITAMENTE**

---

## 🎯 Sobre

Backend FastAPI para gerenciamento de organizações com:
- ✅ Criação de organizações com usuário admin
- ✅ Autenticação JWT
- ✅ Hashing de senhas com Argon2 (SEM limite de 72 bytes!)
- ✅ Banco de dados PostgreSQL
- ✅ Deploy automático no Railway

---

## 🛠️ Stack Tecnológico

### Backend:
- **FastAPI** 0.115.5 - Framework web moderno
- **Python** 3.11 - Linguagem de programação
- **SQLAlchemy** 2.0.36 - ORM assíncrono
- **AsyncPG** 0.30.0 - Driver PostgreSQL assíncrono
- **Pydantic** 2.10.2 - Validação de dados

### Segurança:
- **Argon2-CFFI** 23.1.0 - Hashing de senhas (vencedor PHC 2015)
- **Python-JOSE** 3.3.0 - Tokens JWT
- **Cryptography** - Criptografia

### Banco de Dados:
- **PostgreSQL** 15 - Banco de dados relacional
- **Railway** - Hospedagem do banco

---

## 🚀 Deploy no Railway

### 1. Conectar Repositório
- No Railway, clique em "+ Create" → "GitHub Repo"
- Selecione este repositório
- Railway detecta FastAPI automaticamente

### 2. Conectar PostgreSQL
- Adicione serviço PostgreSQL no mesmo projeto
- Railway cria variável `DATABASE_URL` automaticamente

### 3. Configurar Variáveis de Ambiente
Adicione em Settings → Variables:

```env
DATABASE_URL=postgresql+asyncpg://...  # Automático do PostgreSQL
SECRET_KEY=ft9_super_secret_key_production_2025_very_long_and_secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 4. Deploy Automático
- Push para `main` → Deploy automático
- Railway faz rebuild e restart

**URL de Produção:**
https://ft9-intelligence-backend-production.up.railway.app

---

## 📚 Documentação da API

### Documentação Interativa:
- **Swagger UI:** https://ft9-intelligence-backend-production.up.railway.app/docs
- **ReDoc:** https://ft9-intelligence-backend-production.up.railway.app/redoc

### Guias Completos:

1. **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** ⭐
   - Resumo completo da solução
   - Problema "password cannot be longer than 72 bytes" RESOLVIDO
   - Comparação bcrypt vs Argon2
   - Por que Argon2 é melhor

2. **[API_QUICKSTART.md](API_QUICKSTART.md)** 🚀
   - Guia rápido de uso da API
   - Exemplos de requisições curl
   - Exemplos React/JavaScript
   - Códigos de erro

3. **[TEST_RESULTS.md](TEST_RESULTS.md)** ✅
   - Relatório completo de testes
   - 100% de taxa de sucesso
   - Validações de segurança
   - 6 testes realizados

4. **[README_DEPLOY.md](README_DEPLOY.md)** 🚢
   - Guia detalhado de deploy no Railway
   - Configuração de banco de dados
   - Troubleshooting

---

## 🚀 Quick Start

### Criar Organização:
```bash
curl -X POST https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minha Empresa",
    "email": "contato@empresa.com",
    "admin_email": "admin@empresa.com",
    "admin_password": "senha123",
    "admin_full_name": "Admin Nome"
  }'
```

### Fazer Login:
```bash
curl -X POST https://ft9-intelligence-backend-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@empresa.com&password=senha123"
```

### Obter Organização (Autenticado):
```bash
curl -X GET https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🔐 Segurança

### ⭐ Hashing de Senhas com Argon2:

**POR QUE ARGON2?**
- ✅ **SEM limite de tamanho** para senhas (bcrypt tinha limite de 72 bytes)
- ✅ **Mais seguro** que bcrypt (vencedor PHC 2015)
- ✅ **Resistente a ataques GPU/ASIC**
- ✅ **Recomendado pela OWASP** como padrão moderno

**Configuração:**
- Time cost: 2 iterações
- Memory cost: 102400 KB (~100 MB)
- Parallelism: 8 threads

### Autenticação JWT:
- Tokens assinados com HS256
- Expiração: 7 dias (configurável)
- Payload: user_id + organization_id

### Autorização:
- Role-based Access Control (RBAC)
- Roles: org_admin, user, viewer
- Isolamento por organização

---

## 📊 Endpoints Principais

### Organizações:
- `POST /api/v1/organizations/` - Criar organização (público)
- `GET /api/v1/organizations/me` - Obter minha organização (autenticado)
- `PATCH /api/v1/organizations/me` - Atualizar organização (admin)
- `GET /api/v1/organizations/me/users` - Listar usuários (autenticado)

### Autenticação:
- `POST /api/v1/auth/login` - Login (obter token)
- `POST /api/v1/auth/refresh` - Renovar token
- `GET /api/v1/auth/me` - Obter usuário atual

---

## 📦 Instalação Local

### Pré-requisitos:
- Python 3.11+
- PostgreSQL 15+
- Git

### 1. Clonar Repositório:
```bash
git clone https://github.com/felipetorres-ft/ft9-intelligence-backend.git
cd ft9-intelligence-backend
```

### 2. Criar Ambiente Virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências:
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente:
```bash
cp .env.example .env
```

Editar `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ft9_db
SECRET_KEY=seu_secret_key_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 5. Iniciar Servidor:
```bash
uvicorn main:app --reload
```

Servidor rodando em: http://localhost:8000

---

## 🧪 Testes

### Status dos Testes:
- ✅ **6/6 testes passando** (100% de sucesso)
- ✅ Criação de organizações
- ✅ Login e autenticação
- ✅ Endpoints protegidos
- ✅ Validação de permissões

Ver [TEST_RESULTS.md](TEST_RESULTS.md) para detalhes completos.

---

## 📝 Changelog

### v1.0.0 (09 Nov 2025) ⭐
- ✅ **PROBLEMA RESOLVIDO:** "password cannot be longer than 72 bytes"
- ✅ Substituir bcrypt por Argon2
- ✅ Limpar logs de debug
- ✅ Adicionar documentação completa (3 guias)
- ✅ 100% de testes passando
- ✅ Backend pronto para produção

### v0.1.0 (Inicial)
- ✅ Setup inicial FastAPI
- ✅ Modelos de banco de dados
- ✅ Endpoints básicos
- ✅ Autenticação JWT

---

## 📊 Estrutura do Projeto

```
ft9-intelligence-backend/
├── auth/
│   ├── security.py          # Hashing Argon2 + JWT
│   └── dependencies.py      # Dependências de autenticação
├── database/
│   └── database.py          # Configuração SQLAlchemy
├── models/
│   ├── organization.py      # Model Organization
│   └── user.py              # Model User
├── routers/
│   ├── organization_router.py  # Endpoints de organizações
│   └── auth_router.py       # Endpoints de autenticação
├── schemas/
│   ├── organization.py      # Schemas Pydantic
│   └── user.py              # Schemas Pydantic
├── main.py                  # Aplicação FastAPI
├── requirements.txt         # Dependências Python
├── README.md                # Este arquivo
├── SOLUTION_SUMMARY.md      # ⭐ Resumo da solução
├── API_QUICKSTART.md        # 🚀 Guia rápido da API
├── TEST_RESULTS.md          # ✅ Relatório de testes
└── README_DEPLOY.md         # 🚢 Guia de deploy
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adicionar nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 👥 Autores

- **Felipe Torres** - [@felipetorres-ft](https://github.com/felipetorres-ft)
- **Manus AI** - Assistente de desenvolvimento

---

## 🙏 Agradecimentos

- FastAPI por framework incrível
- Argon2 por algoritmo de hashing seguro
- Railway por plataforma de deploy simples
- OWASP por guidelines de segurança

---

## 📞 Suporte

- **Issues:** https://github.com/felipetorres-ft/ft9-intelligence-backend/issues
- **Documentação:** Ver arquivos `.md` no repositório

---

## 🔗 Links Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Argon2 Docs](https://argon2-cffi.readthedocs.io/)
- [Railway Docs](https://docs.railway.app/)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Status:** ✅ FUNCIONANDO PERFEITAMENTE  
**Última atualização:** 09 Nov 2025  
**Versão:** 1.0.0

---

Desenvolvido com ❤️ pela equipe FT9
