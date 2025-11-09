# 🚀 Início Rápido - FT9 WhatsApp Integration

Este guia te levará de zero a um sistema funcionando em **menos de 15 minutos**.

---

## Pré-requisitos

- Python 3.11+ instalado
- Conta no [Meta for Developers](https://developers.facebook.com/)
- Chave de API da OpenAI

---

## Passo 1: Obter Credenciais da Meta (5 minutos)

1. Acesse [developers.facebook.com/apps](https://developers.facebook.com/apps/)
2. Clique em **"Criar aplicativo"** → Tipo: **"Empresarial"**
3. Dê um nome (ex: "FT9-Test") e associe ao seu Gerenciador de Negócios
4. No painel do app, adicione o produto **"WhatsApp"**
5. Na tela de Início Rápido, copie:
   - ✅ **Token de acesso temporário**
   - ✅ **ID do número de telefone**

---

## Passo 2: Configurar o Projeto (2 minutos)

```bash
# Clone ou extraia o projeto
cd ft9-whatsapp

# Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Copie o arquivo de exemplo e edite
cp .env.example .env
nano .env  # ou use seu editor favorito
```

**Preencha o `.env` com suas credenciais:**

```env
WHATSAPP_API_TOKEN=seu_token_da_meta
WHATSAPP_PHONE_NUMBER_ID=seu_id_de_numero
WHATSAPP_VERIFY_TOKEN=qualquer_string_secreta_que_voce_criar
OPENAI_API_KEY=sua_chave_openai
```

---

## Passo 3: Expor o Servidor Localmente (3 minutos)

```bash
# Em um terminal, inicie o servidor
uvicorn main:app --host 0.0.0.0 --port 8000

# Em outro terminal, instale e rode o ngrok
# Download: https://ngrok.com/download
ngrok http 8000
```

O `ngrok` mostrará uma URL como: `https://abc123.ngrok.io`

---

## Passo 4: Configurar o Webhook na Meta (3 minutos)

1. Volte ao painel do seu app na Meta
2. Vá para **WhatsApp → Configuração**
3. Na seção **Webhooks**, clique em **"Editar"**
4. Preencha:
   - **URL de retorno de chamada:** `https://abc123.ngrok.io/webhook`
   - **Token de verificação:** O mesmo que você colocou no `.env` como `WHATSAPP_VERIFY_TOKEN`
5. Clique em **"Verificar e salvar"**
6. Clique em **"Gerenciar"** e assine o campo **"messages"**

---

## Passo 5: Testar! (2 minutos)

1. No painel da Meta, você verá um número de teste
2. Adicione esse número no seu WhatsApp
3. Envie uma mensagem: **"Olá, FT9!"**
4. Aguarde a resposta inteligente! 🎉

---

## Verificar Logs

No terminal onde o servidor está rodando, você verá logs como:

```
INFO - Received webhook: {...}
INFO - Processing message wamid.xxx from 5511999999999
INFO - AI response generated for user 5511999999999
INFO - Message sent successfully to 5511999999999
```

---

## Solução de Problemas

### Webhook não verifica

- Certifique-se de que o servidor está rodando
- Verifique se o `ngrok` está ativo e a URL está correta
- Confirme que o `WHATSAPP_VERIFY_TOKEN` no `.env` é o mesmo usado na Meta

### Não recebo mensagens

- Verifique se você assinou o evento "messages" no webhook
- Olhe os logs do servidor para ver se o webhook está chegando
- Teste com o endpoint de teste: `curl http://localhost:8000/`

### Erro de autenticação da OpenAI

- Confirme que a `OPENAI_API_KEY` está correta no `.env`
- Verifique se você tem créditos na sua conta OpenAI

---

## Próximos Passos

Agora que está funcionando:

1. Leia o `VISAO_GERAL.md` para entender a arquitetura
2. Leia o `README.md` para instruções de deploy em produção
3. Customize o prompt no arquivo `ai_processor.py` para ajustar o comportamento da IA
4. Quando estiver pronto, faça deploy no Railway ou outra plataforma

---

**Dúvidas?** Todos os arquivos estão comentados e documentados. Explore o código!
