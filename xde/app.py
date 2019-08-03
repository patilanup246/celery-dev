from celery import Celery


app = Celery()
default_config = 'xde.celery_config'
app.config_from_object(default_config)




