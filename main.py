#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2019/11/7 11:18
# @Author  : Kelvin.Ye
# from gevent import monkey; monkey.patch_all()
import sys

from loguru import logger

from app import config as CONFIG
from app import create_app


# 日志级别
LOG_LEVEL = CONFIG.LOG_LEVEL
# 日志文件名称
LOG_FILE_NAME = CONFIG.LOG_FILE.replace('.log', '')

logger.remove()
logger.configure(extra={'traceid': None})
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    colorize=True,
    format='<green>[{time:%Y-%m-%d %H:%M:%S.%f}]</green> <level>[{level}] [{module}:{function}:{line}] [{extra[traceid]}] {message}</level>'
)
logger.add(
    LOG_FILE_NAME + '.{time:YYYY-MM-DD}.log',
    level=LOG_LEVEL,
    diagnose=True,
    backtrace=True,
    rotation='00:00',
    retention='90 days',
    format='[{time:%Y-%m-%d %H:%M:%S.%f}] [{level}] [{module}:{function}:{line}] [{extra[traceid]}] {message}'
)

app = create_app()


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('', 5000), app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
