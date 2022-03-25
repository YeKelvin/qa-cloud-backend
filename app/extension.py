#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : extension.py
# @Time    : 2019/11/7 10:56
# @Author  : Kelvin.Ye
import os
from concurrent.futures import ThreadPoolExecutor

import sqlalchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app import config as CONFIG


FLASK_ENV = os.environ.get('FLASK_ENV')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG')


db = SQLAlchemy()  # type: sqlalchemy
migrate = Migrate()
executor = ThreadPoolExecutor(max_workers=CONFIG.THREAD_EXECUTOR_WORKERS_MAX)


sio_kwargs = {}
if FLASK_ENV == 'development':
    sio_kwargs['cors_allowed_origins'] = '*'
if FLASK_DEBUG == '1':
    sio_kwargs['logger'] = True
    sio_kwargs['engineio_logger'] = True
socketio = SocketIO(**sio_kwargs)
