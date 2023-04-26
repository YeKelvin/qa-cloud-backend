#!/usr/bin/ python3
# @File    : extension.py
# @Time    : 2019/11/7 10:56
# @Author  : Kelvin.Ye
import os
from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.gevent import GeventScheduler
from flask_apscheduler.scheduler import APScheduler
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app import config as CONFIG


FLASK_DEBUG = bool(os.environ.get('FLASK_DEBUG'))

sio_opts = {}
if FLASK_DEBUG:
    sio_opts['cors_allowed_origins'] = '*'

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(**sio_opts)
executor = ThreadPoolExecutor(max_workers=CONFIG.THREAD_EXECUTOR_WORKERS_MAX)
apscheduler = APScheduler() if FLASK_DEBUG else APScheduler(GeventScheduler())
