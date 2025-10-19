"""
Rutas de preguntas
"""
from flask import Blueprint, request, jsonify
from app.auth import require_auth

bp = Blueprint("questions", __name__, url_prefix="/api/v1/questions")


@bp.route("/", methods=["GET"])
def list_questions():
    """
    Lista preguntas del banco (paginado)
    """
    try:
        # TODO: Implementar con repository
        return jsonify({
            "questions": [],
            "total": 0,
            "page": 1
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<question_id>", methods=["GET"])
def get_question(question_id):
    """
    Obtiene una pregunta específica
    """
    try:
        # TODO: Implementar con repository
        return jsonify({"message": "Not implemented"}), 501
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
