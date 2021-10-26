#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2019/11/7 9:39
# @Author  : Kelvin.Ye
import os
from typing import Optional

import orjson
from flask import Flask

from app.extension import db
from app.extension import migrate
from app.extension import socketio
from app.utils import config
from app.utils.log_util import get_logger


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


def set_app(app: Flask):
    global __app__

    __app__ = app


def get_app() -> Optional[Flask]:
    global __app__

    if __app__ is None:
        raise RuntimeError('please call create_app() first')
    return __app__


def configure_flask(app: Flask):
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=get_db_url(),
        SQLALCHEMY_COMMIT_ON_TEARDOWN=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            # 使用将来版本的特性
            'future': True,
            # 连接池实现类
            # 'poolclass': QueuePool,
            # 连接池大小
            # 'pool_size': 10,
            # 连接回收时间，这个值必须要比数据库自身配置的 interactive_timeout 的值小
            # 'pool_recycle': 1000,
            # 预检测池中连接是否有效，并替换无效连接
            # 'pool_pre_ping': True,
            # 会打印输出连接池的异常信息，帮助排查问题
            # 'echo_pool': True,
            # 最大允许溢出连接池大小的连接数量
            # 'max_overflow': 5,
            # 自定义序列化函数
            'json_serializer': orjson_serializer,
            # 自定义反序列化函数
            'json_deserializer': orjson_deserializer
        }
    )


def register_extensions(app: Flask):
    """Register Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    register_socketio(app)


def register_socketio(app: Flask):
    socketio.init_app(app)
    # app运行前加载events，否则handle不到
    from app import socket  # noqa


def register_blueprints(app: Flask):
    """Register Flask blueprints"""
    from app.public.controller import blueprint as public_blueprint
    from app.script.controller import blueprint as script_blueprint
    from app.system.controller import blueprint as system_blueprint
    from app.user.controller import blueprint as user_blueprint

    app.register_blueprint(public_blueprint)
    app.register_blueprint(script_blueprint)
    app.register_blueprint(system_blueprint)
    app.register_blueprint(user_blueprint)


def register_hooks(app: Flask):
    from app import hook

    app.before_request(hook.set_logid)
    app.before_request(hook.set_user)

    app.after_request(hook.record_action)
    app.after_request(hook.cross_domain_access)

    # TODO: 添加errorhandler
    # @app.errorhandler(Exception)
    # def error_handler(e):
    #     ...


def register_shell_context(app: Flask):
    """Register shell context objects"""

    def shell_context():
        return {'db': db}

    app.shell_context_processor(shell_context)


def register_commands(app: Flask):
    """Register Click commands"""
    from app import command

    app.cli.add_command(command.initdb)
    app.cli.add_command(command.initdata)
    app.cli.add_command(command.migrate_sqlite_to_pgsql)


def get_db_url() -> str:
    """获取dbUrl"""
    if 'sqlite' in config.get('db', 'type'):
        return get_sqlite_url()

    return config.get('db', 'url')


def get_sqlite_url():
    return f'sqlite:///{os.path.join(config.get_project_path(), "app")}.db'


def orjson_serializer(obj):
    """
    Note that `orjson.dumps()` return byte array, while sqlalchemy expects string, thus `decode()` call.
    """
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC).decode('utf8')


def orjson_deserializer(val):
    return orjson.loads(val)
