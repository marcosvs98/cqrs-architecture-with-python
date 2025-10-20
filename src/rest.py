from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from exceptions import OrderingServiceException, http_exception_handler
from settings import APPLICATION_NAME
from utils.logger import get_logger

logger = get_logger(__name__)


def init_middlewares(app: FastAPI) -> None:
    """Initialize application middlewares."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def init_routes(app: FastAPI, controllers: list[object]) -> None:
    """Register application routes and exception handlers."""

    start_time = getattr(app.state, 'start_time', datetime.now(timezone.utc))

    @app.get('/', status_code=status.HTTP_200_OK, include_in_schema=False)
    async def health_check() -> dict[str, int]:
        return {'status': status.HTTP_200_OK}

    @app.get('/metrics', include_in_schema=False)
    async def metrics() -> dict[str, int | str]:
        uptime = datetime.now(timezone.utc) - start_time
        return {
            'service': APPLICATION_NAME,
            'uptime_seconds': int(uptime.total_seconds()),
        }

    for controller in controllers:
        app.include_router(controller.router)

    @app.exception_handler(OrderingServiceException)
    @app.exception_handler(Exception)
    async def service_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, OrderingServiceException):
            exception = exc
            await logger.error(
                'Domain exception handled',
                name=exc.name,
                resource=str(request.url.path),
            )
        else:
            await logger.exception('Unhandled exception captured', resource=str(request.url.path))
            exception = OrderingServiceException()
        return await http_exception_handler(request, exception)

    @app.exception_handler(NotImplementedError)
    async def not_implemented_error_handler(
        request: Request, exc: NotImplementedError
    ) -> JSONResponse:
        return JSONResponse(
            content={'error': 'Method Not Allowed.'},
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
