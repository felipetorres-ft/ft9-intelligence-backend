"""
Mercado Pago Configuration
Created by: AI9 Architecture
Date: 2025-11-16
"""

import os
import mercadopago

# Initialize Mercado Pago SDK
sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))

def get_mp_sdk():
    """Get configured Mercado Pago SDK instance"""
    return sdk
