# 🚀 API Quick Start - FT9 Intelligence Backend

## 📍 Base URL
```
https://ft9-intelligence-backend-production.up.railway.app
```

---

## 🔑 Endpoints Principais

### 1. Criar Organização (Público)

**Endpoint:** `POST /api/v1/organizations/`

**Descrição:** Cria uma nova organização com usuário administrador.

**Request:**
```bash
curl -X POST https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minha Empresa",
    "email": "contato@minhaempresa.com",
    "admin_email": "admin@minhaempresa.com",
    "admin_password": "senhaSegura123",
    "admin_full_name": "João Silva"
  }'
```

**Response (201 Created):**
```json
{
  "name": "Minha Empresa",
  "email": "contato@minhaempresa.com",
  "phone": null,
  "address": null,
  "city": null,
  "state": null,
  "id": 18,
  "slug": "minha-empresa",
  "subscription_plan": "starter",
  "subscription_status": "trial",
  "is_active": true,
  "created_at": "2025-11-10T02:30:00.000000Z"
}
```

**Campos Obrigatórios:**
- `name` - Nome da organização
- `email` - Email da organização
- `admin_email` - Email do administrador
- `admin_password` - Senha do administrador
- `admin_full_name` - Nome completo do administrador

**Campos Opcionais:**
- `phone` - Telefone
- `address` - Endereço
- `city` - Cidade
- `state` - Estado

---

### 2. Login (Obter Token)

**Endpoint:** `POST /api/v1/auth/login`

**Descrição:** Autentica usuário e retorna token JWT.

**Request:**
```bash
curl -X POST https://ft9-intelligence-backend-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@minhaempresa.com&password=senhaSegura123"
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. Obter Minha Organização (Autenticado)

**Endpoint:** `GET /api/v1/organizations/me`

**Descrição:** Retorna dados da organização do usuário logado.

**Request:**
```bash
curl -X GET https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Response (200 OK):**
```json
{
  "name": "Minha Empresa",
  "email": "contato@minhaempresa.com",
  "phone": null,
  "address": null,
  "city": null,
  "state": null,
  "id": 18,
  "slug": "minha-empresa",
  "subscription_plan": "starter",
  "subscription_status": "trial",
  "is_active": true,
  "created_at": "2025-11-10T02:30:00.000000Z"
}
```

---

### 4. Atualizar Organização (Admin)

**Endpoint:** `PATCH /api/v1/organizations/me`

**Descrição:** Atualiza dados da organização (apenas admin).

**Request:**
```bash
curl -X PATCH https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+55 11 98765-4321",
    "address": "Rua Exemplo, 123",
    "city": "São Paulo",
    "state": "SP"
  }'
```

**Response (200 OK):**
```json
{
  "name": "Minha Empresa",
  "email": "contato@minhaempresa.com",
  "phone": "+55 11 98765-4321",
  "address": "Rua Exemplo, 123",
  "city": "São Paulo",
  "state": "SP",
  "id": 18,
  "slug": "minha-empresa",
  "subscription_plan": "starter",
  "subscription_status": "trial",
  "is_active": true,
  "created_at": "2025-11-10T02:30:00.000000Z"
}
```

---

### 5. Listar Usuários da Organização (Autenticado)

**Endpoint:** `GET /api/v1/organizations/me/users`

**Descrição:** Lista todos os usuários da organização.

**Request:**
```bash
curl -X GET https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/me/users \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Response (200 OK):**
```json
[
  {
    "id": 42,
    "email": "admin@minhaempresa.com",
    "full_name": "João Silva",
    "role": "org_admin",
    "is_active": true,
    "is_verified": true,
    "organization_id": 18,
    "created_at": "2025-11-10T02:30:00.000000Z"
  }
]
```

---

## 🔐 Autenticação

### Como Usar o Token:

1. **Obter token** via endpoint `/api/v1/auth/login`
2. **Incluir token** no header de todas as requisições autenticadas:
   ```
   Authorization: Bearer SEU_TOKEN_AQUI
   ```

### Exemplo Completo:

```bash
# 1. Criar organização
ORG_RESPONSE=$(curl -s -X POST https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste API",
    "email": "teste@api.com",
    "admin_email": "admin@api.com",
    "admin_password": "senha123",
    "admin_full_name": "Admin Teste"
  }')

echo "Organização criada:"
echo $ORG_RESPONSE | python3 -m json.tool

# 2. Fazer login
TOKEN=$(curl -s -X POST https://ft9-intelligence-backend-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@api.com&password=senha123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token obtido: $TOKEN"

# 3. Usar token para acessar dados
curl -X GET https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/me \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

---

## ❌ Códigos de Erro

### 400 Bad Request
**Causa:** Dados inválidos ou email já cadastrado

**Exemplo:**
```json
{
  "detail": "Email da organização já cadastrado"
}
```

### 401 Unauthorized
**Causa:** Token inválido ou expirado

**Exemplo:**
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
**Causa:** Usuário não tem permissão (ex: não é admin)

**Exemplo:**
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
**Causa:** Recurso não encontrado

**Exemplo:**
```json
{
  "detail": "Organização não encontrada"
}
```

### 500 Internal Server Error
**Causa:** Erro no servidor

**Exemplo:**
```json
{
  "detail": "Erro ao criar organização: ..."
}
```

---

## 📊 Roles (Papéis)

### Tipos de Usuário:

1. **`org_admin`** - Administrador da organização
   - Pode atualizar dados da organização
   - Pode gerenciar usuários
   - Acesso total aos recursos

2. **`user`** - Usuário comum
   - Acesso aos recursos da organização
   - Não pode alterar configurações

3. **`viewer`** - Visualizador
   - Apenas leitura
   - Não pode modificar dados

---

## 🧪 Testando no Frontend

### Exemplo React (usando fetch):

```javascript
// Criar organização
async function createOrganization(data) {
  const response = await fetch(
    'https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Fazer login
async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch(
    'https://ft9-intelligence-backend-production.up.railway.app/api/v1/auth/login',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    }
  );
  
  if (!response.ok) {
    throw new Error('Login falhou');
  }
  
  const data = await response.json();
  return data.access_token;
}

// Obter organização
async function getMyOrganization(token) {
  const response = await fetch(
    'https://ft9-intelligence-backend-production.up.railway.app/api/v1/organizations/me',
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  if (!response.ok) {
    throw new Error('Erro ao obter organização');
  }
  
  return await response.json();
}

// Uso:
try {
  // 1. Criar organização
  const org = await createOrganization({
    name: 'Minha Empresa',
    email: 'contato@empresa.com',
    admin_email: 'admin@empresa.com',
    admin_password: 'senha123',
    admin_full_name: 'Admin Nome',
  });
  console.log('Organização criada:', org);
  
  // 2. Fazer login
  const token = await login('admin@empresa.com', 'senha123');
  console.log('Token:', token);
  
  // 3. Obter dados
  const myOrg = await getMyOrganization(token);
  console.log('Minha organização:', myOrg);
  
} catch (error) {
  console.error('Erro:', error.message);
}
```

---

## 📝 Notas Importantes

### Senhas:
- ✅ **SEM limite de tamanho** (Argon2)
- ✅ Aceita caracteres especiais
- ✅ Case-sensitive
- ⚠️ Recomendado: mínimo 8 caracteres

### Slugs:
- Gerados automaticamente a partir do nome
- Apenas letras minúsculas, números e hífens
- Únicos por organização
- Exemplo: "Minha Empresa" → "minha-empresa"

### Tokens JWT:
- Expiram após 7 dias (padrão)
- Devem ser armazenados com segurança
- Incluir em todas as requisições autenticadas

### Rate Limiting:
- ⚠️ Ainda não implementado
- Recomendado: adicionar limite de requisições

---

## 🔗 Links Úteis

- **Backend URL:** https://ft9-intelligence-backend-production.up.railway.app
- **Documentação Interativa:** https://ft9-intelligence-backend-production.up.railway.app/docs
- **Repositório GitHub:** https://github.com/felipetorres-ft/ft9-intelligence-backend

---

**Última atualização:** 09 Nov 2025  
**Versão da API:** v1
