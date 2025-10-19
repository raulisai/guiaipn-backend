"""
Cliente de autenticación con Supabase
"""
from app.extensions import get_supabase


def verify_token(token: str) -> dict:
    """
    Verifica un token JWT de Supabase
    
    Args:
        token: JWT token de Supabase
        
    Returns:
        dict: Información del usuario si es válido
        
    Raises:
        Exception: Si el token es inválido
    """
    try:
        supabase = get_supabase()
        response = supabase.auth.get_user(token)
        
        if response and response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata
            }
        
        raise Exception("Token inválido")
        
    except Exception as e:
        raise Exception(f"Error verificando token: {str(e)}")


def get_user_profile(user_id: str) -> dict:
    """
    Obtiene el perfil completo de un usuario desde la DB
    
    Args:
        user_id: UUID del usuario
        
    Returns:
        dict: Perfil del usuario
    """
    try:
        supabase = get_supabase()
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        
        if response.data:
            return response.data
        
        return None
        
    except Exception as e:
        print(f"Error obteniendo perfil: {e}")
        return None
