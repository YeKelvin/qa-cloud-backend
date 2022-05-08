#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : config.py
# @Time    : 2021-11-03 22:45:55
# @Author  : Kelvin.Ye
import configparser
import os


# 项目路径
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# 配置文件路径
if 'APP_CONFIG_FILE' not in os.environ:
    APP_CONFIG_FILE = os.path.join(PROJECT_PATH, 'config.ini')
    os.environ['APP_CONFIG_FILE'] = APP_CONFIG_FILE
else:
    APP_CONFIG_FILE = os.environ.get('APP_CONFIG_FILE')


# 配置对象
__config__ = configparser.ConfigParser()
__config__.read(APP_CONFIG_FILE)


# 配置项
# 服务相关配置
SERVICE_HTTP_PROTOCOL = __config__.get('service', 'http.protocol')
SERVICE_HTTP_HOST = __config__.get('service', 'http.host')
SERVICE_HTTP_PORT = __config__.get('service', 'http.port')
BASE_URL = __config__.get('service', 'baseurl')

# 日志相关配置
LOG_FILE = __config__.get('log', 'file')
LOG_LEVEL = __config__.get('log', 'level')
if os.environ.get('FLASK_ENV') == 'development':
    LOG_FILE = 'app.log'

# 数据库相关配置
DB_TYPE = __config__.get('db', 'type')
DB_URL = __config__.get('db', 'url')

# JWT相关配置
JWT_ISSUER = __config__.get('jwt', 'issuer')
JWT_SECRET_KEY = __config__.get('jwt', 'secret.key')
JWT_EXPIRE_TIME = __config__.get('jwt', 'expire.time')

# 雪花算法相关配置
SNOWFLAKE_DATACENTER_ID = __config__.get('snowflake', 'datacenter.id')
SNOWFLAKE_WORKER_ID = __config__.get('snowflake', 'worker.id')
SNOWFLAKE_SEQUENCE = __config__.get('snowflake', 'sequence')

# 线程相关配置
THREAD_EXECUTOR_WORKERS_MAX = int(__config__.get('thread', 'executor.workers.max'))
