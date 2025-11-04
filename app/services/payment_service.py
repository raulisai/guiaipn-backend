"""Servicio para integraciones con Stripe."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import stripe

from app.config import Config


@dataclass
class CheckoutSession:
    """DTO para la respuesta simplificada de Stripe."""

    id: str
    url: str
    status: Optional[str]
    amount_total: Optional[int]
    currency: Optional[str]

    @classmethod
    def from_stripe(cls, session: "stripe.checkout.Session") -> "CheckoutSession":
        return cls(
            id=session.id,
            url=session.url,
            status=getattr(session, "status", None),
            amount_total=getattr(session, "amount_total", None),
            currency=getattr(session, "currency", None),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "amount_total": self.amount_total,
            "currency": self.currency,
        }


class PaymentService:
    """Encapsula la lógica de pagos con Stripe."""

    def __init__(self) -> None:
        api_key = Config.STRIPE_API_KEY
        if not api_key:
            raise RuntimeError("Stripe API key no configurada")

        stripe.api_key = api_key

        self._default_price_id = Config.STRIPE_PRICE_ID
        self._success_url = Config.STRIPE_SUCCESS_URL
        self._cancel_url = Config.STRIPE_CANCEL_URL

    def create_checkout_session(self, price_id: Optional[str] = None, quantity: int = 1) -> dict:
        """Crea una sesión de Checkout en Stripe."""
        selected_price = price_id or self._default_price_id
        if not selected_price:
            raise ValueError("Stripe Price ID no configurado")

        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")

        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                       'price': 'price_1SOc8IIRx2YI9IwfL7TFhn1v',
                       'quantity': 1,
                    }
                ],
                success_url=self._success_url,
                cancel_url=self._cancel_url,
            )
        except stripe.error.StripeError as exc:  # type: ignore[attr-defined]
            message = getattr(exc, "user_message", None) or str(exc)
            raise RuntimeError(f"Error creando sesión de pago en Stripe: {message}") from exc

        return CheckoutSession.from_stripe(session).to_dict()
