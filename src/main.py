import uvicorn
import settings
from app import create_app

app = create_app()

app_base_configs = {
    'host': '0.0.0.0',
    'port': settings.PORT,
    'workers': settings.UVICORN_WORKERS,
    'access_log': True,
}

if __name__ == '__main__':
    uvicorn.run('main:app', **app_base_configs)
