#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2019/11/7 9:39
# @Author  : Kelvin.Ye
import os

from flask import Flask

from app import user, system, script, command, hook  # user一定要排第一位，不然会报循环引用的Error
from app.utils import config
from app.utils.log_util import get_logger
from app.extension import db, migrate, socketio

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
        SQLALCHEMY_DATABASE_URI=get_db_url(),
        SQLALCHEMY_COMMIT_ON_TEARDOWN=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
    )


def register_extensions(app):
    """Register Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    register_socketio(app)


def register_socketio(app):
    socketio.init_app(app)
    # app运行前加载events，否则handle不到
    from app import socket  # noqa


def register_blueprints(app):
    """Register Flask blueprints"""
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
    """Register shell context objects"""
    def shell_context():
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands"""
    app.cli.add_command(command.initdb)
    app.cli.add_command(command.initdata)


def get_db_url() -> str:
    """获取dbUrl"""
    db_type = config.get('db', 'type')
    if db_type.startswith('sqlite'):
        return get_sqlite_url()

    username = config.get('db', 'username')
    password = config.get('db', 'password')
    address = config.get('db', 'address')
    name = config.get('db', 'name')
    db_url = f'{db_type}://{username}:{password}@{address}/{name}'
    return db_url


def get_sqlite_url():
    name = config.get('db', 'name')
    return f'sqlite:///{os.path.join(config.get_project_path(), name)}.db'
