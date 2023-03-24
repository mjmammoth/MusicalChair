import uvicorn

from config import settings
from app_instances import web_app
from router import router

web_app.include_router(router)

if __name__ == '__main__':
    if settings.DEPLOYMENT_ENV == 'local':
        print('Running in local mode')
    else:
        print('Running in GCP Native mode')

    uvicorn.run('main:web_app', host='0.0.0.0',
                port=settings.PORT, reload=True)
