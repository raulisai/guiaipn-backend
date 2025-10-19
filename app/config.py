"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base de la aplicación"""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    ENV = os.getenv("FLASK_ENV", "development")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    
    # Rate Limiting
    MAX_CONNECTIONS_PER_IP = int(os.getenv("MAX_CONNECTIONS_PER_IP", 5))
    RATE_LIMIT_QUESTIONS = int(os.getenv("RATE_LIMIT_QUESTIONS", 10))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    
    # Session
    SESSION_TTL = 1800  # 30 minutos
    CACHE_TTL = 86400   # 24 horas
    
    @staticmethod
    def validate():
        """Valida que las variables críticas estén configuradas"""
        required = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "OPENAI_API_KEY"
        ]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Faltan variables de entorno: {', '.join(missing)}")
