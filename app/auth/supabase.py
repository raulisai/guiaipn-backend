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


def create_user_profile(user_id: str, email: str, full_name: str = None, avatar_url: str = None) -> dict:
    """
    Crea un perfil inicial para un nuevo usuario con valores por defecto
    
    Args:
        user_id: UUID del usuario
        email: Email del usuario
        full_name: Nombre completo (opcional)
        avatar_url: URL del avatar (opcional)
        
    Returns:
        dict: Perfil creado
        
    Raises:
        Exception: Si hay error al crear el perfil
    """
    try:
        supabase = get_supabase()
        
        # Crear perfil con valores por defecto
        profile_data = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "plan_type": "free",
            "credits_remaining": 10,
            "credits_total": 10,
            "daily_limit": 5,
            "daily_used": 0,
            "preferred_language": "es",
            "learning_level": "medium"
        }
        
        response = supabase.table("profiles").insert(profile_data).execute()
        
        if not response.data:
            raise Exception("Error al crear perfil")
        
        return response.data[0]
        
    except Exception as e:
        raise Exception(f"Error creando perfil: {str(e)}")


def initialize_user_progress(user_id: str) -> list:
    """
    Inicializa el progreso del usuario para todas las materias principales
    
    Args:
        user_id: UUID del usuario
        
    Returns:
        list: Lista de registros de progreso creados
        
    Raises:
        Exception: Si hay error al inicializar el progreso
    """
    try:
        supabase = get_supabase()
        
        # Materias principales del IPN
        subjects = [
            "matematicas",
            "fisica",
            "quimica",
            "biologia",
            "historia",
            "geografia",
            "literatura",
            "ingles"
        ]
        
        # Crear registro de progreso para cada materia
        progress_data = [
            {
                "user_id": user_id,
                "subject": subject,
                "total_practiced": 0,
                "total_correct": 0,
                "mastery_level": 0.00,
                "streak_days": 0
            }
            for subject in subjects
        ]
        
        response = supabase.table("user_progress").insert(progress_data).execute()
        
        if not response.data:
            raise Exception("Error al inicializar progreso")
        
        return response.data
        
    except Exception as e:
        raise Exception(f"Error inicializando progreso: {str(e)}")
