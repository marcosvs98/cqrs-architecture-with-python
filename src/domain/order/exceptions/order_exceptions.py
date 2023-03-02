from exceptions import CommonException


class OrderAlreadyCancelledException(CommonException):
    pass


class OrderAlreadyPaidException(CommonException):
    pass


class PaymentNotVerifiedException(CommonException):
    pass


class EntityNotFound(CommonException):
    pass


class EntityOutdated(CommonException):
    pass
