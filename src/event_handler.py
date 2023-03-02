from fastapi import FastAPI
from database import get_mongo_db


async def startup(app: FastAPI):
    app.state.event_source = get_mongo_db(app.state.event_source_config)


async def shutdown(app: FastAPI):
    app.state.event_source.close()
