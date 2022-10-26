#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2019/11/7 9:39
# @Author  : Kelvin.Ye
import os
from typing import Optional

import orjson
from apscheduler.events import EVENT_ALL
from apscheduler.events import EVENT_JOB_ADDED
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.events import EVENT_JOB_MAX_INSTANCES
from apscheduler.events import EVENT_JOB_MODIFIED
from apscheduler.events import EVENT_JOB_REMOVED
from apscheduler.events import EVENT_JOB_SUBMITTED
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask

from app import config as CONFIG
from app.extension import apscheduler
from app.extension import db
from app.extension import migrate
from app.extension import socketio


__app__ = None

FLASK_ENV = os.environ.get('FLASK_ENV')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG')


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
        raise RuntimeError('Please call create_app() first!!!')
    return __app__


def configure_flask(app: Flask):
    # https://viniciuschiele.github.io/flask-apscheduler/rst/api.html
    scheduler_api_enabled = False
    if FLASK_ENV == 'development':
        scheduler_api_enabled = True
        scheduler_executors = {'default': {'type': 'threadpool', 'max_workers': 10}}
    else:
        scheduler_executors = {'default': {'type': 'gevent'}}

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=CONFIG.DB_URL,
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
        },
        SCHEDULER_API_ENABLED=scheduler_api_enabled,
        SCHEDULER_EXECUTORS=scheduler_executors,
        SCHEDULER_JOBSTORES={'default': SQLAlchemyJobStore(url=CONFIG.DB_URL)},
        SCHEDULER_JOB_DEFAULTS={'coalesce': True, 'max_instances': CONFIG.SCHEDULE_JOB_INSTANCES_MAX},
        SCHEDULER_TIMEZONE='Asia/Shanghai'
    )


def register_extensions(app: Flask):
    """Register Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    register_socketio(app)
    register_apscheduler(app)


def register_socketio(app: Flask):
    # 服务启动前加载 events
    from app import socket  # noqa
    socketio.init_app(app)


def register_apscheduler(app: Flask):
    from app.schedule import event
    apscheduler.add_listener(event.handle_event_all, EVENT_ALL)
    apscheduler.add_listener(event.handle_job_added, EVENT_JOB_ADDED)
    apscheduler.add_listener(event.handle_job_modified, EVENT_JOB_MODIFIED)
    apscheduler.add_listener(event.handle_job_removed, EVENT_JOB_REMOVED)
    apscheduler.add_listener(event.handle_job_submitted, EVENT_JOB_SUBMITTED)
    apscheduler.add_listener(event.handle_job_max_instances, EVENT_JOB_MAX_INSTANCES)
    apscheduler.add_listener(event.handle_job_executed, EVENT_JOB_EXECUTED)
    apscheduler.add_listener(event.handle_job_error, EVENT_JOB_ERROR)
    apscheduler.init_app(app)
    apscheduler.start()


def register_blueprints(app: Flask):
    """Register Flask blueprints"""
    from app.public.controller import blueprint as public_blueprint
    from app.schedule.controller import blueprint as schedule_blueprint
    from app.script.controller import blueprint as script_blueprint
    from app.system.controller import blueprint as system_blueprint
    from app.usercenter.controller import blueprint as usercenter_blueprint

    app.register_blueprint(public_blueprint)
    app.register_blueprint(schedule_blueprint)
    app.register_blueprint(script_blueprint)
    app.register_blueprint(system_blueprint)
    app.register_blueprint(usercenter_blueprint)


def register_hooks(app: Flask):
    from app import hook

    app.before_request(hook.set_trace_id)
    app.before_request(hook.set_user)
    app.before_request(hook.add_operation_log)

    if FLASK_ENV == 'development':
        app.after_request(hook.cross_domain_access)


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
    app.cli.add_command(command.dropdb)
    app.cli.add_command(command.create_single_table)
    app.cli.add_command(command.initp)


def orjson_serializer(obj):
    """
    Note that `orjson.dumps()` return byte array, while sqlalchemy expects string, thus `decode()` call.
    """
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC).decode('utf8')


def orjson_deserializer(val):
    return orjson.loads(val)
