"""
Control de rate limiting
"""
from app.extensions import get_redis
from app.config import Config


class RateLimiter:
    """Gestiona límites de tasa de peticiones"""
    
    def __init__(self):
        self.redis = get_redis()
        self.window = Config.RATE_LIMIT_WINDOW
        self.max_requests = Config.RATE_LIMIT_QUESTIONS
    
    def check_limit(self, user_id: str, action: str = "questions") -> tuple:
        """
        Verifica si un usuario ha excedido el límite
        
        Args:
            user_id: ID del usuario
            action: Tipo de acción
            
        Returns:
            tuple: (allowed, remaining, retry_after)
        """
        key = f"rate_limit:{user_id}:{action}"
        
        try:
            current = self.redis.get(key)
            
            if current is None:
                # Primera petición en la ventana
                self.redis.setex(key, self.window, 1)
                return True, self.max_requests - 1, 0
            
            current = int(current)
            
            if current >= self.max_requests:
                # Límite excedido
                ttl = self.redis.ttl(key)
                return False, 0, ttl
            
            # Incrementar contador
            self.redis.incr(key)
            return True, self.max_requests - current - 1, 0
            
        except Exception as e:
            print(f"Error en rate limiter: {e}")
            # En caso de error, permitir la petición
            return True, self.max_requests, 0
    
    def reset_limit(self, user_id: str, action: str = "questions"):
        """
        Resetea el límite de un usuario
        
        Args:
            user_id: ID del usuario
            action: Tipo de acción
        """
        key = f"rate_limit:{user_id}:{action}"
        self.redis.delete(key)
