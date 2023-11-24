from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from bootstrap import initialize_order_controller
from exceptions import CommonException
from settings import APPLICATION_NAME


def init_middlewares(app: FastAPI):
    # Configuration of CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def init_routes(app: FastAPI):
    # Definition of the health check endpoint
    @app.get('/', status_code=200, response_model=dict)
    async def health_check() -> dict:
        return {'status': 200}

    # Initialization of the order controller and definition of routes
    order_controller = initialize_order_controller()
    app.include_router(order_controller.router, tags=['order'], prefix='/api/v1/order')

    # Custom exception handlers
    @app.exception_handler(CommonException)
    async def service_exception_handler(request: Request, error: CommonException) -> JSONResponse:
        return JSONResponse(error.to_dict(), status_code=error.code)

    @app.exception_handler(NotImplementedError)
    async def not_implemented_error_handler(request, exc: NotImplementedError) -> JSONResponse:
        return JSONResponse(content={'error': 'Method Not Allowed.'}, status_code=405)


def create_app():
    # Creation of the FastAPI application instance
    app = FastAPI(
        title=APPLICATION_NAME,
        description='FastAPI application using hexagonal architecture',
    )

    # Initialization of middlewares and routes
    init_middlewares(app)
    init_routes(app)

    # Addition of pagination support
    add_pagination(app)

    return app
