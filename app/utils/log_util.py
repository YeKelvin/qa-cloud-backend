#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/11/7 10:12
# @Author  : Kelvin.Ye
import logging
from logging.config import dictConfig

from app.utils import config

# 日志格式
LOG_FORMAT = '[%(asctime)s][%(levelname)s][%(threadName)s][%(name)s.%(funcName)s %(lineno)d] %(message)s'

# logger配置
dictConfig({
    'version': 1,
    'root': {
        'propagate': 0,
        'level': config.get('log', 'level'),  # handler的level会覆盖掉这里的level
        'handlers': ['console', 'file']
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://flask.logging.wsgi_errors_stream'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'encoding': 'utf-8',
            'filename': config.get('log', 'name')
        }
    },
    'formatters': {
        'default': {
            'format': LOG_FORMAT
        }
    }
})

# 日志级别
LEVEL = config.get('log', 'level')

# 日志文件名称
LOG_FILE_NAME = config.get('log', 'name')

# 日志格式
FORMATTER = logging.Formatter(LOG_FORMAT)

# 输出到控制台
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 写入日志文件
FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)


def get_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    logger.addHandler(FILE_HANDLER)
    return logger


class WerkzeugLogFilter(logging.Filter):
    def __init__(self):
        super(WerkzeugLogFilter, self).__init__()

    def filter(self, record):
        print(record.__dict__)
        return True


class SendAnywhereLogFilter(logging.Filter):
    def __init__(self):
        super(WerkzeugLogFilter, self).__init__()

    def filter(self, record):
        print(record.__dict__)
        return True
