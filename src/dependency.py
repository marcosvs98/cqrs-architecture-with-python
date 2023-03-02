from fastapi import Request


async def get_mongo_db(request: Request):
    mongo_db = request.app.state.mongo_db
    return mongo_db
