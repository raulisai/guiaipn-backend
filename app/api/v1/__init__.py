"""
API v1
"""

from app.api.v1 import auth_routes, question_routes, session_routes, payment_routes

__all__ = [
    "auth_routes",
    "question_routes",
    "session_routes",
    "payment_routes",
]
