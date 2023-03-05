import uuid

from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface
from domain.payment.value_objects import PaymentId


class PayPalPaymentAdapter(PaymentAdapterInterface):
    async def new_payment(self, total_price: float) -> PaymentId:
        return PaymentId(str(uuid.uuid4()))

    async def verify_payment(self, payment_id: PaymentId) -> bool:
        return True
