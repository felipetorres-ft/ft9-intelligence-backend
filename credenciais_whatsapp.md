# Credenciais WhatsApp Business API - FT9

## ✅ Informações Obtidas

### App Information
- **App Name:** FT9 Business Messaging
- **App ID:** 787793967589184
- **App Type:** Business
- **App Mode:** Development

### Business Portfolio
- **Nome:** FT9 Intelligence
- **Business ID:** 1818030975740061

### WhatsApp Business Account
- **WhatsApp Business Account ID:** 1505215831318900
- **Account Type:** Test WhatsApp Business Account

### Test Phone Number
- **Test Number:** +1 555 166 7990
- **Phone Number ID:** 839615479241121
- **Validade:** 90 dias (mensagens gratuitas)

### Access Token
- **Status:** Autorização completa realizada
- **Permissões:** whatsapp_business_management, whatsapp_business_messaging
- **Nota:** Token temporário precisa ser gerado via interface (válido por 24h)

---

## 🔄 Como Gerar o Access Token

O token temporário pode ser gerado de duas formas:

### Opção 1: Via Interface Web (Recomendado)
1. Acessar: https://developers.facebook.com/apps/787793967589184/whatsapp-business/wa-dev-console/
2. Clicar em "Generate access token"
3. Selecionar "Test WhatsApp Business Account"
4. Copiar o token gerado

### Opção 2: Via Graph API Explorer
1. Acessar: https://developers.facebook.com/tools/explorer/
2. Selecionar o app "FT9 Business Messaging"
3. Adicionar permissões: whatsapp_business_management, whatsapp_business_messaging
4. Gerar User Access Token
5. Copiar o token

---

## 📝 Próximos Passos

1. **Gerar o Access Token** via uma das opções acima
2. **Configurar o arquivo .env** do protótipo com as credenciais
3. **Iniciar o servidor** FastAPI
4. **Expor publicamente** com ngrok
5. **Configurar webhook** na Meta
6. **Testar** enviando mensagem no WhatsApp

---

## 🔗 Links Úteis

- **App Dashboard:** https://developers.facebook.com/apps/787793967589184/
- **WhatsApp API Setup:** https://developers.facebook.com/apps/787793967589184/whatsapp-business/wa-dev-console/
- **Business Manager:** https://business.facebook.com/settings/whatsapp-business-accounts/1505215831318900
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/

---

## ⚠️ Importante

- Token temporário expira em **24 horas**
- Número de teste válido por **90 dias**
- Mensagens gratuitas durante o período de teste
- Para produção, será necessário adicionar número real e método de pagamento
