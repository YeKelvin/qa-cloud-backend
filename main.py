#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2019/11/7 11:18
# @Author  : Kelvin.Ye
import logging
import sys

from loguru import logger

from app import config as CONFIG
from app import create_app
from app.utils.log_util import InterceptHandler
from app.utils.log_util import console_formatter
from app.utils.log_util import file_formatter


# logging 输出至 loguru
logging.basicConfig(handlers=[InterceptHandler()], level=0)


# 日志级别
LOG_LEVEL = CONFIG.LOG_LEVEL
# 日志文件名称
LOG_FILE_NAME = CONFIG.LOG_FILE.replace('.log', '')


# 配置loguru
logger.remove()
logger.configure(extra={'traceid': None})
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    colorize=True,
    format=console_formatter,
)
logger.add(
    LOG_FILE_NAME + '.{time:YYYY-MM-DD}.log',
    level=LOG_LEVEL,
    diagnose=True,
    backtrace=True,
    rotation='00:00',
    retention='90 days',
    format=file_formatter
)


# 创建app
app = create_app()


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('', 5000), app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
