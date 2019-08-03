from celery import Celery
from flask import Flask


class FlaskCelery(object):
    """Flask Celery extension
    To set Celery config, use prefix CELERY_ with Celery config keys in Flask application config, for examples:
    - broker_url = 'xxx' -> CELERY_BROKER_URL = 'xxx'
    - imports = ('foo', 'bar') -> CELERY_IMPORTS = ('foo', 'bar')

    Or you can use CELERY_CONFIG_MODULE env variable to set the Celery config module.
    export CELERY_CONFIG_MODULE=/path/to/celeryconfig.py
    Usage:
        app = Flask(__name__)
        fc = FlaskCelery(app)

        # Celery instance
        celery = fc.celery
    """
    CELERY_CONFIG_KEY_PREFIX = 'CELERY_'

    app = None
    celery = None

    def __init__(self, app):
        if app is not None:
            self.init_app(app)

    def init_app(self, app, **kwargs):
        if not isinstance(app, Flask):
            raise ValueError('app must be a Flask app')
        self.app = app
        self.celery = self._create_celery(**kwargs)

    def _create_celery(self, **kwargs):
        """Create a Celery instance bound with this app.
        :rtype: Celery
        """
        celery = Celery(self.app.import_name, **kwargs)
        celery.config_from_object(self._extract_celery_config(), silent=True)
        celery.config_from_envvar('CELERY_CONFIG_MODULE', silent=True)
        celery.Task = self.create_task_cls(celery.Task)
        return celery

    def create_task_cls(self, base_task_cls):
        """Create Celery Task class bound with the Flask app based on a specific Task class"""
        app = self.app

        class ContextTask(base_task_cls):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super(ContextTask, self).__call__(*args, **kwargs)

        return ContextTask

    def _extract_celery_config(self):
        """Extracts Celery config keys from config of the app."""
        keys = filter(lambda key: key.startswith(self.CELERY_CONFIG_KEY_PREFIX), self.app.config.keys())
        return dict((key[7:].lower(), self.app.config[key]) for key in keys)
