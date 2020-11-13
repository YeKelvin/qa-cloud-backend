#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : app.py
# @Time    : 2019/11/7 11:02
# @Author  : Kelvin.Ye
import os
import flask_monitoringdashboard as dashboard

from flasgger import Swagger
from flask import Flask

from server import user, system, command, hook, script
from server.extension import db, swagger, migrate
from server.common.utils import config
from server.common.utils.log_util import get_logger

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
    return app


def get_app_instance() -> Flask:
    global __app__
    if __app__ is None:
        __app__ = create_app()
    return __app__


def configure_flask(app):
    app.config.from_mapping(
        DEV='development',
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI=__generate_db_url(),
        SQLALCHEMY_COMMIT_ON_TEARDOWN=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
    )


def register_extensions(app):
    """Register Flask extensions.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    dashboard.bind(app)


def register_blueprints(app):
    """Register Flask blueprints.
    """
    app.register_blueprint(user.controllers.blueprint)
    app.register_blueprint(system.controllers.blueprint)
    app.register_blueprint(script.controllers.blueprint)


def register_hooks(app):
    app.before_request(hook.set_logid)
    app.before_request(hook.set_user)
    app.after_request(hook.record_action)
    app.after_request(hook.cross_domain_access)


def register_shell_context(app):
    """Register shell context objects.
    """

    def shell_context():
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands.
    """
    app.cli.add_command(command.initdb)
    app.cli.add_command(command.initdata)


def register_swagger(app):
    swagger.config = Swagger.DEFAULT_CONFIG.copy().update({
        'title': '测试平台 RESTful API',  # 配置大标题
        'description': 'Test Platform Server RESTful API',  # 配置公共描述内容
        'host': '0.0.0.0',  # 请求域名
        'swagger_ui_bundle_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js',
        'swagger_ui_standalone_preset_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js',
        'jquery_js': '//unpkg.com/jquery@2.2.4/dist/jquery.min.js',
        'swagger_ui_css': '//unpkg.com/swagger-ui-dist@3/swagger-ui.css',
    })
    swagger.init_app(app)


def __generate_db_url() -> str:
    """生成 db url
    """
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
