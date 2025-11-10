#!/usr/bin/env python3
"""Testar hash de senha"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash de senha"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        while len(password_truncated.encode('utf-8')) > 72:
            password_truncated = password_truncated[:-1]
    else:
        password_truncated = password
    return pwd_context.hash(password_truncated)

# Testar
test_password = "ft9demo2025"
print(f"Senha: {test_password}")
print(f"Tamanho: {len(test_password)} chars, {len(test_password.encode('utf-8'))} bytes")

try:
    hashed = get_password_hash(test_password)
    print(f"✅ Hash gerado com sucesso!")
    print(f"Hash: {hashed[:50]}...")
except Exception as e:
    print(f"❌ Erro: {e}")
