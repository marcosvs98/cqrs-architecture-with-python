from datetime import datetime, timezone

from fastapi import FastAPI

from containers import AppContainer
from rest import init_middlewares, init_routes
from settings import APPLICATION_NAME


def create_app() -> FastAPI:
    container = AppContainer()
    container.init_resources()
    container.wire(modules=[__name__])

    # Creation of the FastAPI application instance
    app = FastAPI(
        title=APPLICATION_NAME,
        description='FastAPI application using cqrs architecture',
    )
    app.state.start_time = datetime.now(timezone.utc)

    # Initialization of middlewares and routes
    init_middlewares(app)
    init_routes(
        app,
        [
            container.order_controller(),
            container.order_query_controller(),
        ],
    )

    return app
