#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : app.py
# @Time    : 2019/11/7 11:02
# @Author  : Kelvin.Ye
import logging
import os

from flask import Flask

from server import user, system, commands, hooks
from server.extensions import db
from server.utils import config
from server.utils.log_util import get_logger, CONSOLE_HANDLER, LEVEL

log = get_logger(__name__)

__app__ = None


def create_app() -> Flask:
    app = Flask(__name__)
    configure_flask(app)
    # configure_logger()
    register_extensions(app)
    register_blueprints(app)
    register_hooks(app)
    register_shellcontext(app)
    register_commands(app)
    return app


def get_app_instance() -> Flask:
    global __app__
    if __app__ is None:
        __app__ = create_app()
    return __app__


def configure_flask(app):
    app.config.from_mapping(
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI=__generate_db_url(),
        SQLALCHEMY_COMMIT_ON_TEARDOWN=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False  # 是否打印SQL语句
        # UPLOAD_FOLDER=config.get('file', 'upload.folder')
    )


def configure_logger():
    logger = logging.getLogger()
    logger.addHandler(CONSOLE_HANDLER)
    logger.setLevel(LEVEL)


def register_extensions(app):
    """Register Flask extensions.
    """
    db.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints.
    """
    app.register_blueprint(user.route.blueprint)
    app.register_blueprint(system.route.blueprint)


def register_hooks(app):
    app.before_request(hooks.set_logid)
    app.before_request(hooks.set_user)
    app.after_request(hooks.record_action)


def register_shellcontext(app):
    """Register shell context objects.
    """
    shell_context = {"db": db}
    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands.
    """
    app.cli.add_command(commands.initdb)
    app.cli.add_command(commands.initdata)


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
