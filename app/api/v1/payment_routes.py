"""Rutas para pagos con Stripe."""
from flask import Blueprint, jsonify, request

from app.auth.decorators import require_auth
from app.services.payment_service import PaymentService

bp = Blueprint("payments", __name__, url_prefix="/api/v1/payments")


@bp.route("/checkout-session", methods=["POST"])
@require_auth
def create_checkout_session():
    """Crea una sesión de checkout en Stripe."""
    data = request.get_json(silent=True) or {}
    price_id = data.get("price_id")
    quantity = data.get("quantity", 1)

    try:
        quantity_int = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "El campo 'quantity' debe ser un entero"}), 400

    payment_service = PaymentService()

    try:
        session = payment_service.create_checkout_session(price_id=price_id, quantity=quantity_int)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 502
    except Exception as err:  # pragma: no cover - fallback para errores inesperados
        return jsonify({"error": f"Error creando sesión de pago: {err}"}), 500

    return jsonify(session), 201
