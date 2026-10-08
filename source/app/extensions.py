from celery import Celery
import collections
import json
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO, Namespace
from flask_sqlalchemy import SQLAlchemy
from functools import partial

from app.configuration import Config
from app.flask_dropzone import Dropzone

cache = Cache()

SQLALCHEMY_ENGINE_OPTIONS = {
    "json_deserializer": partial(json.loads, object_pairs_hook=collections.OrderedDict),
    "pool_pre_ping": True
}

db = SQLAlchemy(engine_options=SQLALCHEMY_ENGINE_OPTIONS)  # flask-sqlalchemy

bc = Bcrypt()  # flask-bcrypt

lm = LoginManager()  # flask-loginmanager

ma = Marshmallow() # Init marshmallow

dropzone = Dropzone()

celery = Celery(__name__, config_source=getattr(Config, 'CELERY'))

socket_io = SocketIO()
