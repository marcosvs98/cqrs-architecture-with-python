import abc
from decimal import Decimal

from domain.payment.model.value_objects import PaymentId


class PaymentAdapterInterface(abc.ABC):
    """Abstraction for payment provider integration."""

    @abc.abstractmethod
    async def new_payment(self, total_price: Decimal) -> PaymentId:
        """Create a new payment for the given total price."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def verify_payment(self, payment_id: PaymentId) -> bool:
        """Verify whether a payment has been successfully completed."""
        raise NotImplementedError()
