# coding:utf8

import os
import logging
from logging.handlers import TimedRotatingFileHandler

from flask.logging import default_handler
from flask import Flask, request

from demo import form


def page_not_found(e):
    return "page not found", 400


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        record.req_method = request.method
        return super().format(record)


def init_logging_handler(app):
    log_path = os.path.join(app.instance_path, 'app.log')
    handler = TimedRotatingFileHandler(log_path, when='midnight', interval=1)
    formatter = RequestFormatter(
      '[%(asctime)s] %(remote_addr)s requested %(url)s [%(req_method)s] '
      '%(levelname)s in %(module)s:  %(message)s'
    )
    handler.setFormatter(formatter)
    return handler


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY=os.urandom(16),
            )

    app.config.from_pyfile('config.py', silent=True)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    app.register_error_handler(404, page_not_found)

    app.register_blueprint(form.bp)

    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False
    handler = init_logging_handler(app)
    app.logger.removeHandler(default_handler)
    app.logger.addHandler(handler)

    return app
