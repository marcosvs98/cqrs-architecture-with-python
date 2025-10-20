import uuid
from decimal import Decimal

from domain.payment.model.value_objects import PaymentId
from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface


class PayPalPaymentAdapter(PaymentAdapterInterface):
    """Mock PayPal adapter for demonstration purposes."""

    async def new_payment(self, total_price: Decimal) -> PaymentId:
        """Simulate creation of a new PayPal payment."""
        return PaymentId(str(uuid.uuid4()))

    async def verify_payment(self, payment_id: PaymentId) -> bool:
        """Simulate verification of a PayPal payment."""
        return True
