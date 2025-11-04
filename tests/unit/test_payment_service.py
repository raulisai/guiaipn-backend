"""Tests unitarios para PaymentService."""
from types import SimpleNamespace

import pytest

from app.config import Config
from app.services.payment_service import PaymentService, stripe as stripe_sdk


class TestPaymentService:
    """Conjunto de pruebas para la integración con Stripe."""

    def test_create_checkout_session_success(self, monkeypatch):
        monkeypatch.setattr(Config, "STRIPE_API_KEY", "sk_test_123")
        monkeypatch.setattr(Config, "STRIPE_PRICE_ID", "price_default")
        monkeypatch.setattr(Config, "STRIPE_SUCCESS_URL", "https://example.com/success")
        monkeypatch.setattr(Config, "STRIPE_CANCEL_URL", "https://example.com/cancel")
        captured = {}

        def fake_create(**kwargs):
            captured["kwargs"] = kwargs
            return SimpleNamespace(
                id="cs_test",
                url="https://stripe.com/checkout",
                status="open",
                amount_total=1500,
                currency="mxn",
            )

        monkeypatch.setattr(
            "app.services.payment_service.stripe.checkout.Session.create",
            fake_create,
        )

        service = PaymentService()
        result = service.create_checkout_session(quantity=2)

        assert result == {
            "id": "cs_test",
            "url": "https://stripe.com/checkout",
            "status": "open",
            "amount_total": 1500,
            "currency": "mxn",
        }
        assert captured["kwargs"]["line_items"][0]["price"] == "price_default"
        assert captured["kwargs"]["line_items"][0]["quantity"] == 2
        assert captured["kwargs"]["success_url"] == "https://example.com/success"
        assert captured["kwargs"]["cancel_url"] == "https://example.com/cancel"
        assert stripe_sdk.api_key == "sk_test_123"

    def test_create_checkout_session_custom_price(self, monkeypatch):
        monkeypatch.setattr(Config, "STRIPE_API_KEY", "sk_test_456")
        monkeypatch.setattr(Config, "STRIPE_PRICE_ID", None)
        monkeypatch.setattr(Config, "STRIPE_SUCCESS_URL", "https://example.com/success")
        monkeypatch.setattr(Config, "STRIPE_CANCEL_URL", "https://example.com/cancel")

        captured = {}

        def fake_create(**kwargs):
            captured["kwargs"] = kwargs
            return SimpleNamespace(id="cs_test", url="https://stripe.com/checkout", status=None, amount_total=None, currency=None)

        monkeypatch.setattr(
            "app.services.payment_service.stripe.checkout.Session.create",
            fake_create,
        )

        service = PaymentService()
        result = service.create_checkout_session(price_id="price_custom")

        assert result["id"] == "cs_test"
        assert captured["kwargs"]["line_items"][0]["price"] == "price_custom"

    def test_create_checkout_session_missing_price(self, monkeypatch):
        monkeypatch.setattr(Config, "STRIPE_API_KEY", "sk_test")
        monkeypatch.setattr(Config, "STRIPE_PRICE_ID", None)
        monkeypatch.setattr(Config, "STRIPE_SUCCESS_URL", "https://example.com/success")
        monkeypatch.setattr(Config, "STRIPE_CANCEL_URL", "https://example.com/cancel")

        service = PaymentService()

        with pytest.raises(ValueError) as exc:
            service.create_checkout_session()

        assert "Stripe Price ID" in str(exc.value)

    def test_create_checkout_session_invalid_quantity(self, monkeypatch):
        monkeypatch.setattr(Config, "STRIPE_API_KEY", "sk_test")
        monkeypatch.setattr(Config, "STRIPE_PRICE_ID", "price_default")
        monkeypatch.setattr(Config, "STRIPE_SUCCESS_URL", "https://example.com/success")
        monkeypatch.setattr(Config, "STRIPE_CANCEL_URL", "https://example.com/cancel")

        service = PaymentService()

        with pytest.raises(ValueError) as exc:
            service.create_checkout_session(quantity=0)

        assert "cantidad debe ser mayor a cero" in str(exc.value)

    def test_payment_service_requires_api_key(self, monkeypatch):
        monkeypatch.setattr(Config, "STRIPE_API_KEY", None)

        with pytest.raises(RuntimeError) as exc:
            PaymentService()

        assert "Stripe API key" in str(exc.value)
