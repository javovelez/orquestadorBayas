from celery import Celery

celery_app = Celery(
    'orquestador',
    broker='redis://redis:6379/0',  # Broker (Redis)
    backend='redis://redis:6379/1',  # Backend para resultados
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)

from .tasks import *