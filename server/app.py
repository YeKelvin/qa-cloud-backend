#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : app.py
# @Time    : 2019/11/7 11:02
# @Author  : Kelvin.Ye
import os

from flasgger import Swagger
from flask import Flask

from server import user, system, script, command, hook  # user一定要排第一位，不然会报循环引用的Error
from server.common.utils import config
from server.utils.log_util import get_logger
from server.extension import db, migrate, socketio, swagger

log = get_logger(__name__)

__app__ = None


def create_app() -> Flask:
    app = Flask(__name__)
    configure_flask(app)
    register_extensions(app)
    register_blueprints(app)
    register_hooks(app)
    register_shell_context(app)
    register_commands(app)
    set_app(app)
    return app


def set_app(app):
    global __app__
    __app__ = app


def get_app() -> Flask:
    global __app__
    if __app__ is None:
        raise RuntimeError('please call create_app() first')
    return __app__


def configure_flask(app):
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=__generate_db_url__(),
        SQLALCHEMY_COMMIT_ON_TEARDOWN=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
    )


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    register_socketio(app)
    # register_swagger(app)


def register_socketio(app):
    socketio.init_app(app)
    from server import socket  # noqa  # app运行前加载events，否则handle不到


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(user.controllers.blueprint)
    app.register_blueprint(system.controllers.blueprint)
    app.register_blueprint(script.controllers.blueprint)


def register_hooks(app):
    app.before_request(hook.set_logid)
    app.before_request(hook.set_user)

    app.after_request(hook.record_action)
    app.after_request(hook.cross_domain_access)

    # TODO: 添加errorhandler
    # @app.errorhandler(Exception)
    # def error_handler(e):
    #     ...


def register_shell_context(app):
    """Register shell context objects."""
    def shell_context():
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(command.initdb)
    app.cli.add_command(command.initdata)


def register_swagger(app):
    swagger.config = Swagger.DEFAULT_CONFIG.copy().update({
        'title':
        '测试平台 RESTful API',  # 配置大标题
        'description':
        'Test Platform Server RESTful API',  # 配置公共描述内容
        'host':
        '0.0.0.0',  # 请求域名
        'swagger_ui_bundle_js':
        '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js',
        'swagger_ui_standalone_preset_js':
        '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js',
        'jquery_js':
        '//unpkg.com/jquery@2.2.4/dist/jquery.min.js',
        'swagger_ui_css':
        '//unpkg.com/swagger-ui-dist@3/swagger-ui.css',
    })
    swagger.init_app(app)


def __generate_db_url__() -> str:
    """生成 db url"""
    db_type = config.get('db', 'type')
    if not db_type.startswith('sqlite'):
        username = config.get('db', 'username')
        password = config.get('db', 'password')
        address = config.get('db', 'address')
        name = config.get('db', 'name')
        db_url = f'{db_type}://{username}:{password}@{address}/{name}'
        return db_url
    else:
        address = config.get_project_path()
        name = config.get('db', 'name')
        db_url = f'{db_type}:///{os.path.join(address, name)}.db'
        return db_url
