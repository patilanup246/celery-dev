# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""

from flask import Blueprint, Flask
from werkzeug.utils import find_modules, import_string

from xde.config import default as default_config
from xde.core.extensions import bcrypt, cache, db
from xde.core.middleware import HTTPMethodOverrideMiddleware
from xde.helpers import setup_logging
from xde.helpers.preconditions import check_not_empty, check_not_none


def create_app(package_name, config=None, auto_discover_blueprints=False):
    app = Flask(package_name)
    app.config.from_object(default_config)
    app.config.from_envvar('XDE_CONFIG_MODULE', silent=True)
    app.config.from_object(config)

    setup_logging(app)

    register_extensions(app)

    if auto_discover_blueprints:
        discover_blueprints(app, package_name)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    return app


def register_extensions(app):
    """Register core Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)


def discover_blueprints(app, package_name):
    check_not_none(app)
    check_not_empty(package_name)
    for name in find_modules(package_name, recursive=True):
        mod = import_string(name)
        for item in dir(mod):
            item = getattr(mod, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
