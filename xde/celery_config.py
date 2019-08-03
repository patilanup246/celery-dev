CELERY_BROKER_URL = 'pyampq://guest:guest@localhost:5672/'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CELERY_IMPORTS = [
    'xde.tasks'
]
