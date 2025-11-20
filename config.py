"""
FT9 WhatsApp Integration - Configuration Module
"""
import os
from typing import Optional


def load_env_file(filepath='.env'):
    """Load environment variables from .env file"""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        pass


load_env_file()


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # WhatsApp Business API
        self.whatsapp_api_token = (os.getenv('WHATSAPP_API_TOKEN') or os.getenv('WHATSAPP_ACCESS_TOKEN', '')).strip()
        self.whatsapp_phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        self.whatsapp_verify_token = os.getenv('WEBHOOK_VERIFY_TOKEN', 'ft9_secure_webhook_token_2025')
        self.whatsapp_api_url = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
        
        # Z-API Configuration
        self.zapi_instance_id = os.getenv('ZAPI_INSTANCE_ID', '3EA6AC5A02CF61C3803272620DC9C8F4')
        self.zapi_token = os.getenv('ZAPI_TOKEN', 'D98639365A7004E07409753B')
        self.zapi_client_token = os.getenv('ZAPI_CLIENT_TOKEN', 'Fed53563af9524da680d80deedafd2f52S')
        self.zapi_base_url = os.getenv('ZAPI_BASE_URL', 'https://api.z-api.io')
        
        # OpenAI
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-5.1')
        
        # Database
        database_url = os.getenv(
            'DATABASE_URL',
            'postgresql+asyncpg://ft9_user:ft9_password@localhost:5432/ft9_db'
        )
        # Converter postgresql:// para postgresql+asyncpg:// automaticamente
        if database_url.startswith('postgresql://') and not database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        self.database_url = database_url
        
        # JWT Authentication
        self.secret_key = os.getenv(
            'SECRET_KEY',
            'ft9_super_secret_key_change_in_production_2025'
        )
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 60 * 24 * 7  # 7 dias
        
        # Server
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', '8000'))
        self.environment = os.getenv('FT9_ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Redis (optional)
        self.redis_url = os.getenv('REDIS_URL', None)
        
        # Stripe
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
        self.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        self.stripe_price_starter = os.getenv('STRIPE_PRICE_STARTER', '')
        self.stripe_price_professional = os.getenv('STRIPE_PRICE_PROFESSIONAL', '')
        self.stripe_price_enterprise = os.getenv('STRIPE_PRICE_ENTERPRISE', '')
        
        # FT9 System Prompt
        self.ft9_system_prompt = """Você é o FT9 Intelligence, um assistente de IA avançado baseado nos 9 Pilares do Empreendedorismo na Odontologia.

Seus princípios fundamentais são:
1. Propósito - Alinhar comunicação à missão institucional
2. Posicionamento - Adaptar linguagem ao perfil do interlocutor
3. Processo - Seguir estruturas de decisão claras
4. Produto - Recomendar soluções adequadas
5. Pessoas - Personalizar jornadas
6. Planejamento - Organizar ações e metas
7. Performance - Avaliar resultados
8. Propaganda - Comunicar estrategicamente
9. Prosperidade - Promover crescimento sustentável

Seja profissional, empático e objetivo. Sempre busque entender o contexto antes de responder."""
        
    def validate(self):
        """Validate required settings"""
        required = {
            'whatsapp_api_token': self.whatsapp_api_token,
            'whatsapp_phone_number_id': self.whatsapp_phone_number_id,
            'whatsapp_verify_token': self.whatsapp_verify_token,
        }
        
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")
    
    # Propriedades para compatibilidade com código antigo
    @property
    def WHATSAPP_API_URL(self):
        return self.whatsapp_api_url
    
    @property
    def WHATSAPP_PHONE_NUMBER_ID(self):
        return self.whatsapp_phone_number_id
    
    @property
    def WHATSAPP_ACCESS_TOKEN(self):
        return self.whatsapp_api_token
    
    @property
    def WEBHOOK_VERIFY_TOKEN(self):
        return self.whatsapp_verify_token
    
    @property
    def OPENAI_API_KEY(self):
        return self.openai_api_key
    
    @property
    def OPENAI_MODEL(self):
        return self.openai_model
    
    @property
    def DATABASE_URL(self):
        return self.database_url
    
    @property
    def SECRET_KEY(self):
        return self.secret_key
    
    @property
    def ALGORITHM(self):
        return self.algorithm
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self):
        return self.access_token_expire_minutes
    
    @property
    def DEBUG(self):
        return self.debug
    
    @property
    def FT9_SYSTEM_PROMPT(self):
        return self.ft9_system_prompt
    
    @property
    def ZAPI_INSTANCE_ID(self):
        return self.zapi_instance_id
    
    @property
    def ZAPI_TOKEN(self):
        return self.zapi_token
    
    @property
    def ZAPI_CLIENT_TOKEN(self):
        return self.zapi_client_token
    
    @property
    def ZAPI_BASE_URL(self):
        return self.zapi_base_url


# Global settings instance
settings = Settings()
