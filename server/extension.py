#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : extensions.py
# @Time    : 2019/11/7 10:56
# @Author  : Kelvin.Ye
from concurrent.futures import ThreadPoolExecutor

from flasgger import Swagger
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
swagger = Swagger()
migrate = Migrate()
executor = ThreadPoolExecutor(max_workers=10)
socketio = SocketIO(cors_allowed_origins='*', logger=True, engineio_logger=True)
