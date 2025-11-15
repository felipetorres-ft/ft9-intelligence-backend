# 🔧 CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE - RAILWAY
## Implementado conforme especificação dos programadores
## Data: 15/11/2025

---

## 📋 VARIÁVEIS NECESSÁRIAS

### 1. OPENAI_API_KEY ⚠️ CRÍTICO

**Descrição:** Chave de API da OpenAI para gerar embeddings e respostas RAG

**Como obter:**
1. Acessar: https://platform.openai.com/api-keys
2. Criar nova chave de API (Project API Key)
3. Copiar a chave (começa com `sk-proj-...`)

**Como configurar no Railway:**
```bash
# Via Dashboard Railway:
1. Acessar: https://railway.app
2. Selecionar projeto: ft9-intelligence-backend
3. Ir em: Variables
4. Adicionar variável:
   - Nome: OPENAI_API_KEY
   - Valor: sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
5. Clicar em: Deploy

# Via Railway CLI:
railway variables set OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Validação:**
```python
import os
print(f"OPENAI_API_KEY configurada: {bool(os.getenv('OPENAI_API_KEY'))}")
```

---

### 2. DATABASE_URL ✅ JÁ CONFIGURADO

**Descrição:** URL de conexão com PostgreSQL (Railway configura automaticamente)

**Formato:**
```
postgresql://user:password@host:port/database
```

**Verificar:**
```bash
railway variables get DATABASE_URL
```

---

### 3. CORS_ORIGINS ⚠️ IMPORTANTE

**Descrição:** Domínios permitidos para requisições CORS

**Valor recomendado:**
```
https://www.ft9intelligence.com,https://ft9-frontend.vercel.app
```

**Como configurar:**
```bash
railway variables set CORS_ORIGINS="https://www.ft9intelligence.com,https://ft9-frontend.vercel.app"
```

---

### 4. WHATSAPP_TOKEN ⏳ PENDENTE

**Descrição:** Token permanente do WhatsApp Business API

**Localização do token:**
```
/home/ubuntu/FT9_BACKUP_ATUALIZADO_13NOV2025/TOKEN_WHATSAPP/TOKEN_WHATSAPP_PERMANENTE_13NOV2025.txt
```

**Como configurar:**
```bash
# Copiar token do arquivo e executar:
railway variables set WHATSAPP_TOKEN="EAALMfpOVJ0ABP0kmvNpz5d6k2pin9cYZCgOZAEZBgB..."
```

---

## 🚀 PASSOS PARA CONFIGURAÇÃO COMPLETA

### Passo 1: Acessar Railway
```bash
# Login via CLI
railway login

# Ou acessar via browser:
# https://railway.app/project/b7f3c0f5-9f0f-4e5e-8f3e-3e3e3e3e3e3e
```

### Passo 2: Adicionar OPENAI_API_KEY
```bash
railway variables set OPENAI_API_KEY="sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### Passo 3: Configurar CORS
```bash
railway variables set CORS_ORIGINS="https://www.ft9intelligence.com,https://ft9-frontend.vercel.app"
```

### Passo 4: Adicionar WHATSAPP_TOKEN (quando disponível)
```bash
railway variables set WHATSAPP_TOKEN="EAALMfpOVJ0ABP0kmvNpz5d6k2pin9cYZCgOZAEZBgB..."
```

### Passo 5: Verificar variáveis configuradas
```bash
railway variables
```

### Passo 6: Fazer deploy
```bash
railway up
```

---

## 🔍 VERIFICAÇÃO PÓS-DEPLOY

### 1. Verificar logs
```bash
railway logs
```

**Buscar por:**
- ✅ "OPENAI_API_KEY configurada: True"
- ✅ "Database initialized successfully"
- ✅ "Uvicorn running on http://0.0.0.0:8080"

### 2. Testar endpoint de health
```bash
curl https://ft9-intelligence-backend-production.up.railway.app/
```

**Resposta esperada:**
```json
{
  "status": "online",
  "service": "FT9 WhatsApp Integration with AI9 Engine",
  "version": "2.0.0"
}
```

### 3. Testar endpoint de knowledge
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://ft9-intelligence-backend-production.up.railway.app/api/v1/knowledge/count
```

**Resposta esperada:**
```json
{
  "count": 0
}
```

---

## ⚠️ TROUBLESHOOTING

### Erro: "OPENAI_API_KEY não configurada"
**Solução:**
```bash
railway variables set OPENAI_API_KEY="sk-proj-..."
railway up
```

### Erro: "CORS policy"
**Solução:**
```bash
railway variables set CORS_ORIGINS="https://www.ft9intelligence.com"
railway up
```

### Erro: "extension 'vector' is not available"
**Solução:**
- Railway já tem pgvector instalado por padrão
- Verificar se a migração foi executada:
```bash
railway run python database/init_pgvector.py
```

---

## 📊 CHECKLIST DE CONFIGURAÇÃO

- [ ] OPENAI_API_KEY adicionada
- [ ] CORS_ORIGINS configurado
- [ ] WHATSAPP_TOKEN adicionado (opcional)
- [ ] Deploy realizado
- [ ] Logs verificados
- [ ] Endpoints testados
- [ ] Frontend atualizado com nova API

---

## 📞 SUPORTE

**Documentação Railway:**
- https://docs.railway.app/reference/variables

**Documentação OpenAI:**
- https://platform.openai.com/docs/api-reference

**Documentação pgvector:**
- https://github.com/pgvector/pgvector

---

**Guia criado por:** AI9  
**Data:** 15/11/2025  
**Versão:** 1.0
