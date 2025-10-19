"""
Módulo de autenticación con Supabase
"""
from app.auth.supabase import verify_token
from app.auth.decorators import require_auth

__all__ = ["verify_token", "require_auth"]
