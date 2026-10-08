#  IRIS Source Code
#  Copyright (C) 2021 - Airbus CyberSecurity (SAS)
#  ir@cyberactionlab.net
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import boto3
import collections
import json
import logging as logger
import os
import urllib.parse
from flask import Flask
from flask import session
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO, Namespace
from flask_sqlalchemy import SQLAlchemy
from functools import partial
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from werkzeug.middleware.proxy_fix import ProxyFix

from app.configuration import Config
from app.extensions import bc
from app.extensions import cache
from app.extensions import celery
from app.extensions import db
from app.extensions import dropzone
from app.extensions import lm
from app.extensions import ma
from app.extensions import socket_io
from app.iris_engine.tasker.celery import init_celery
from app.iris_engine.access_control.oidc_handler import get_oidc_client

config = Config

class ReverseProxied(object):
    def __init__(self, flask_app):
        self._app = flask_app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO', None)
        if scheme is not None:
            environ['wsgi.url_scheme'] = scheme
        return self._app(environ, start_response)


class AlertsNamespace(Namespace):
    def on_connect(self):
        # This namespace has no client-initiated events to gate with a per-event
        # decorator - it is only ever used for server-broadcast events (e.g. new_alert),
        # namespace-wide. Without a connect-time check, any client could connect (cors is
        # wide open) and passively receive that reconnaissance data (CWE-306).
        from flask import request as flask_request
        from app.util import is_user_authenticated
        if not is_user_authenticated(flask_request):
            return False


APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'templates/')

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
LOG_FORMAT = '%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s :: %(message)s'
LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

logger.basicConfig(level=logger.INFO, format=LOG_FORMAT, datefmt=LOG_TIME_FORMAT)

# app = Flask(__name__)


def _refresh_session_permissions():
    # Deferred import: app.iris_engine.access_control.utils reads current_app at import
    # time, so it can't be imported at module load here, before the Flask app exists.
    from flask_login import current_user
    from app.iris_engine.access_control.utils import ac_get_effective_permissions_of_user
    session['permissions'] = ac_get_effective_permissions_of_user(current_user)
    return session['permissions']


def ac_current_user_has_permission(*permissions):
    """
    Return True if current user has permission
    """
    # Always recompute rather than trusting whatever was cached at login: group/role
    # changes and admin-initiated revocations must take effect on the very next request,
    # not only once the session cookie eventually expires (CWE-613).
    perms = _refresh_session_permissions()
    for permission in permissions:
        if perms & permission.value == permission.value:
            return True

    return False


def ac_current_user_has_manage_perms():
    perms = _refresh_session_permissions()
    if perms != 1 and perms & 0x1FFFFF0 != 0:
        return True
    return False


s3 = boto3.client(
    's3',
    endpoint_url=getattr(config, 'FS_ENDPOINT', None),
    aws_access_key_id=getattr(config, 'FS_ACCESS_KEY', None),
    aws_secret_access_key=getattr(config, 'FS_SECRET_KEY', None),
    config=boto3.session.Config(
        signature_version="s3v4",
        connect_timeout=10,
        read_timeout=20,
        retries={"max_attempts": 2, "mode": "standard"}
    ),
    region_name="rustfs"
)

store = HttpExposedFileSystemStore(
    path='images',
    prefix='/static/assets/images/'
)

oidc_client = None
if getattr(config, 'AUTHENTICATION_TYPE', None) == "oidc":
    oidc_client = get_oidc_client(config)

# TODO: figure out where this goes in factory pattern
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db.session.remove()

def create_app(config=None):
    # logger.warn("Initializing Flask app")
    app = Flask(__name__)
    app.logger.setLevel(logger.INFO)

    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    app.jinja_env.filters['unquote'] = lambda u: urllib.parse.unquote(u)
    app.jinja_env.filters['tojsonsafe'] = lambda u: json.dumps(u, indent=4, ensure_ascii=False)
    app.jinja_env.filters['tojsonindent'] = lambda u: json.dumps(u, indent=4)
    app.jinja_env.filters['escape_dots'] = lambda u: u.replace('.', '[.]')
    app.jinja_env.globals.update(user_has_perm=ac_current_user_has_permission)
    app.jinja_env.globals.update(user_has_manage_perms=ac_current_user_has_manage_perms)
    app.jinja_options["autoescape"] = lambda _: True

    app.jinja_env.autoescape = True
    app.config.from_object('app.configuration.Config')

    if config:
        app.config.update(config)

    # app.config['RUN_POST_INIT'] = run_post_init

    # Initialize application state for extensions
    logger.info("Initializing application extensions")
    cache.init_app(app)
    lm.init_app(app)
    db.init_app(app)
    bc.init_app(app)
    ma.init_app(app)
    dropzone.init_app(app)
    init_celery(app)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    app.wsgi_app = store.wsgi_middleware(app.wsgi_app)

    socket_io.init_app(
        app,
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
        async_mode='gevent',
        cors_allowed_origins="*",
    )
    alerts_namespace = AlertsNamespace('/alerts')
    socket_io.on_namespace(alerts_namespace)

    with app.app_context():

        from app import views

        return app

