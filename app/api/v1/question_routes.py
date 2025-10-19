"""
Rutas de preguntas de examen
"""
from flask import Blueprint, request, jsonify
from app.auth import require_auth
from app.services.exam_service import ExamService

bp = Blueprint("questions", __name__, url_prefix="/api/v1/questions")


@bp.route("/random", methods=["GET"])
@require_auth
def get_random_question(current_user):
    """
    Obtiene una pregunta aleatoria por materia
    
    Query params:
        - subject: string (required) - matematicas, fisica, quimica, etc
        - difficulty: string (optional) - easy, medium, hard
    """
    try:
        subject = request.args.get("subject")
        difficulty = request.args.get("difficulty")
        
        if not subject:
            return jsonify({"error": "El parámetro 'subject' es requerido"}), 400
        
        exam_service = ExamService()
        question = exam_service.get_random_question(subject, difficulty)
        
        if not question:
            return jsonify({"error": "No se encontraron preguntas para esta materia"}), 404
        
        return jsonify(question), 200
        
    except Exception as e:
        print(f"Error obteniendo pregunta aleatoria: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/<question_id>/answer", methods=["POST"])
@require_auth
def submit_answer(current_user, question_id):
    """
    Valida la respuesta del usuario a una pregunta
    
    Body:
        - user_answer: string (required) - a, b, c, d
    """
    try:
        data = request.get_json()
        
        if not data or "user_answer" not in data:
            return jsonify({"error": "El campo 'user_answer' es requerido"}), 400
        
        user_answer = data["user_answer"].strip().lower()
        
        if user_answer not in ["a", "b", "c", "d"]:
            return jsonify({"error": "La respuesta debe ser a, b, c o d"}), 400
        
        exam_service = ExamService()
        result = exam_service.validate_answer(question_id, user_answer)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error validando respuesta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/", methods=["GET"])
def list_questions():
    """
    Lista preguntas del banco (paginado)
    
    Query params:
        - page: int (optional) - Página actual (default: 1)
        - limit: int (optional) - Resultados por página (default: 20)
        - subject: string (optional) - Filtrar por materia
    """
    try:
        from app.repositories.question_repo import QuestionRepository
        
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        subject = request.args.get("subject")
        
        question_repo = QuestionRepository()
        
        if subject:
            questions = question_repo.get_by_subject(subject, limit)
            total = len(questions)
        else:
            offset = (page - 1) * limit
            questions = question_repo.get_all(limit, offset)
            total = len(questions)  # En producción, hacer count() separado
        
        return jsonify({
            "questions": questions,
            "total": total,
            "page": page,
            "limit": limit
        }), 200
        
    except Exception as e:
        print(f"Error listando preguntas: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/<question_id>", methods=["GET"])
def get_question(question_id):
    """
    Obtiene una pregunta específica por ID
    """
    try:
        from app.repositories.question_repo import QuestionRepository
        
        question_repo = QuestionRepository()
        question = question_repo.get_by_id(question_id)
        
        if not question:
            return jsonify({"error": "Pregunta no encontrada"}), 404
        
        return jsonify(question), 200
        
    except Exception as e:
        print(f"Error obteniendo pregunta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
