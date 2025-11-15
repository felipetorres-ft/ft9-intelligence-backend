# auth.py – alias das funções de segurança
from auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user,
    require_role,
)
