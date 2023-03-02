import abc
from domain.payment.value_objects import PaymentId


class PaymentAdapterInterface(abc.ABC):
    @abc.abstractmethod
    async def new_payment(self, total_price: float) -> PaymentId:
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_payment(self, payment_id: PaymentId) -> bool:
        raise NotImplementedError
