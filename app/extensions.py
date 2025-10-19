"""
Inicialización de extensiones (Redis, Supabase, SocketIO)
"""
import redis
from supabase import create_client, Client
from flask_socketio import SocketIO
from flask_cors import CORS


# Instancias globales
redis_client = None
supabase_client: Client = None


def init_extensions(app, socketio: SocketIO):
    """
    Inicializa todas las extensiones de la aplicación
    """
    global redis_client, supabase_client
    
    # Validar configuración
    from app.config import Config
    Config.validate()
    
    # CORS
    CORS(app, resources={
        r"/*": {
            "origins": Config.CORS_ORIGINS,
            "supports_credentials": True
        }
    })
    
    # Redis
    redis_client = redis.from_url(
        Config.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    
    # Supabase
    supabase_client = create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_ANON_KEY
    )
    
    # SocketIO
    socketio.init_app(
        app,
        cors_allowed_origins=Config.CORS_ORIGINS,
        async_mode="threading",
        logger=Config.DEBUG,
        engineio_logger=Config.DEBUG
    )
    
    # Test connections
    try:
        redis_client.ping()
        print("✓ Redis conectado")
    except redis.exceptions.ConnectionError as e:
        print(f"✗ Error conectando a Redis: {e}")
        raise RuntimeError(f"No se pudo conectar a Redis: {e}")
    
    print("✓ Supabase inicializado")
    print("✓ SocketIO inicializado")


def get_redis():
    """Obtiene el cliente de Redis"""
    return redis_client


def get_supabase():
    """Obtiene el cliente de Supabase"""
    return supabase_client
