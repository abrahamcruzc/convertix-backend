from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker="amqp://guest:guest@localhost:5672//",
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.convert_image']
)

celery_app.conf.task_routes = {
    "app.tasks.convert_image.convert_image": "main-queue"  
}

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)