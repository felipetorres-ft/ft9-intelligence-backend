# 🚀 Instruções de Deploy Manual - FT9 Intelligence Platform

## Opção 1: Deploy via Railway (Recomendado)

### Passo 1: Criar Conta no Railway
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub ou email
3. Verifique sua conta

### Passo 2: Criar Novo Projeto
1. Click em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Autorize o Railway a acessar seus repositórios
4. Selecione o repositório `ft9-whatsapp`

### Passo 3: Adicionar PostgreSQL
1. No projeto, click em "New"
2. Selecione "Database" → "Add PostgreSQL"
3. Railway criará automaticamente o banco
4. A variável `DATABASE_URL` será configurada automaticamente

### Passo 4: Configurar Variáveis de Ambiente
No painel do serviço, vá em "Variables" e adicione:

```env
# Obrigatórias
SECRET_KEY=sua_chave_secreta_super_longa_e_aleatoria_aqui
OPENAI_API_KEY=sk-...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Opcionais para Beta
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
WHATSAPP_API_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
```

### Passo 5: Deploy
1. Railway detectará automaticamente o `Dockerfile`
2. Click em "Deploy"
3. Aguarde 3-5 minutos

### Passo 6: Gerar Domínio Público
1. Vá em "Settings" → "Networking"
2. Click em "Generate Domain"
3. Copie a URL gerada (ex: `ft9-backend.up.railway.app`)

### Passo 7: Inicializar Banco de Dados
1. No Railway, vá em "Settings" → "Deploy"
2. Em "Custom Start Command", adicione:
   ```
   python init_db_production.py && uvicorn main_multitenant:app --host 0.0.0.0 --port $PORT
   ```
3. Ou execute manualmente via Railway CLI

---

## Opção 2: Deploy via Render

### Passo 1: Criar Conta no Render
1. Acesse [render.com](https://render.com)
2. Faça login com GitHub

### Passo 2: Criar Web Service
1. Click em "New +" → "Web Service"
2. Conecte seu repositório GitHub
3. Configure:
   - **Name:** ft9-backend
   - **Environment:** Docker
   - **Plan:** Free (para teste)

### Passo 3: Adicionar PostgreSQL
1. Click em "New +" → "PostgreSQL"
2. Configure:
   - **Name:** ft9-database
   - **Plan:** Free
3. Copie a "Internal Database URL"

### Passo 4: Configurar Variáveis
Adicione as mesmas variáveis da Opção 1, mais:
```env
DATABASE_URL=postgresql://... (da etapa anterior)
```

### Passo 5: Deploy
1. Click em "Create Web Service"
2. Aguarde o build (5-10 minutos)

---

## Opção 3: Deploy via Heroku

### Passo 1: Instalar Heroku CLI
```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### Passo 2: Criar App
```bash
cd /path/to/ft9-whatsapp
heroku create ft9-backend
```

### Passo 3: Adicionar PostgreSQL
```bash
heroku addons:create heroku-postgresql:essential-0
```

### Passo 4: Configurar Variáveis
```bash
heroku config:set SECRET_KEY=sua_chave_secreta
heroku config:set OPENAI_API_KEY=sk-...
# ... outras variáveis
```

### Passo 5: Deploy
```bash
git push heroku master
```

### Passo 6: Inicializar Banco
```bash
heroku run python init_db_production.py
```

---

## Verificação Pós-Deploy

### Testar API
```bash
# Substituir URL pela sua
curl https://sua-url.railway.app/

# Testar login
curl -X POST https://sua-url.railway.app/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ft9.com.br", "password": "ft9demo"}'
```

### Acessar Documentação
Abra no navegador:
```
https://sua-url.railway.app/docs
```

---

## Troubleshooting

### Erro: "Application failed to respond"
- Verifique se a variável `PORT` está configurada
- Verifique logs: `railway logs` ou no painel web

### Erro: "Database connection failed"
- Verifique se `DATABASE_URL` está configurada
- Verifique se o PostgreSQL está rodando

### Erro: "Module not found"
- Verifique se `requirements.txt` está completo
- Force rebuild no Railway

---

## Custos Estimados

| Plataforma | Custo Mensal |
|:---|---:|
| **Railway** | $5-10 (Hobby Plan) |
| **Render** | $0-7 (Free/Starter) |
| **Heroku** | $7-25 (Eco/Basic) |

**Recomendação:** Railway (melhor custo-benefício + facilidade)
