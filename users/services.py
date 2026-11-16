import stripe
from django.conf import settings

# Инициализация клиента Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str, description: str) -> str:
    """Создает продукт в Stripe и возвращает его ID."""
    product = stripe.Product.create(
        name=name,
        description=description or "Оплата курса на LMS Platform",
    )
    return product.id


def create_stripe_price(product_id: str, amount: float) -> str:
    """
    Создает цену для продукта в Stripe.
    ВАЖНО: Stripe принимает сумму в копейках/центах, поэтому умножаем на 100.
    """
    amount_in_cents = int(amount * 100)
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount_in_cents,
        currency="rub",
    )
    return price.id


def create_stripe_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Создает сессию оплаты и возвращает ID сессии и ссылку на оплату."""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],  # type: ignore[call-arg]
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {
        "id": session.id,
        "url": session.url,
    }


def get_stripe_session_status(session_id: str) -> str:
    """Получает статус сессии оплаты из Stripe."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
    except stripe.error.StripeError as e:
        raise ValueError(f"Ошибка Stripe: {str(e)}")
