# Railway Deploy - Notas Importantes

## Métodos de Deploy

1. **One-Click Template** (mais rápido)
2. **GitHub Repository** (recomendado)
3. **Railway CLI**
4. **Dockerfile**

## Passos para Deploy via GitHub:

1. Criar conta no Railway
2. New Project → Deploy from GitHub repo
3. Selecionar repositório
4. Deploy Now
5. Networking → Generate Domain (para URL pública)

## Configurações Necessárias:

### Dockerfile (já temos)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main_multitenant:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

### Variáveis de Ambiente (configurar no Railway):
- DATABASE_URL
- SECRET_KEY
- OPENAI_API_KEY
- STRIPE_SECRET_KEY (opcional para beta)
- WHATSAPP_API_TOKEN (opcional para beta)

## PostgreSQL no Railway:

1. New Project → Add Service → Database → PostgreSQL
2. Railway fornece automaticamente a DATABASE_URL
3. Conectar ao serviço FastAPI

## Próximos Passos:

1. ✅ Preparar repositório GitHub
2. ✅ Criar Dockerfile otimizado
3. ✅ Configurar railway.toml
4. ✅ Deploy no Railway
5. ✅ Configurar PostgreSQL
6. ✅ Testar endpoints
