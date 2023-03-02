from fastapi import FastAPI
from fastapi_pagination import add_pagination
from settings import APPLICATION_NAME
from adapters.rest_adapter import init_routes, init_middlewares


def create_app():
    app = FastAPI(
        title=APPLICATION_NAME,
        description='FastAPI application using hexagonal architecture',
    )

    init_middlewares(app)
    init_routes(app)
    add_pagination(app)

    return app
