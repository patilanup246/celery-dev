from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cache = Cache()
bcrypt = Bcrypt()
