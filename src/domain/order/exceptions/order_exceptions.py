from exceptions import CommonException


class OrderAlreadyCancelledException(CommonException):
    """Exception raised when attempting to cancel an order that has already been cancelled."""


class OrderAlreadyPaidException(CommonException):
    """Exception raised when attempting to pay for an order that has already been paid."""


class PaymentNotVerifiedException(CommonException):
    """Exception raised when a payment is not verified for an order."""


class EntityNotFound(CommonException):
    """Exception raised when attempting to access an entity that does not exist."""


class EntityOutdated(CommonException):
    """Exception raised when attempting to perform an operation on an outdated entity."""


class PersistenceError(CommonException):
    """Exception raised for errors related to persistence (e.g., database errors)."""
