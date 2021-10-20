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
        'propagate': False,
        'level': config.get('log', 'level'),  # handler的level会覆盖掉这里的level
        'handlers': ['console', 'file']
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
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

# 配置werkzeug日志
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False
werkzeug_logger.setLevel(logging.INFO)
for handler in werkzeug_logger.handlers:
    werkzeug_logger.removeHandler(handler)
werkzeug_logger.addHandler(CONSOLE_HANDLER)
werkzeug_logger.addHandler(FILE_HANDLER)

# 配置sqlalchemy日志
sqlalchemy_logger = logging.getLogger('sqlalchemy')
sqlalchemy_logger.propagate = False
sqlalchemy_logger.setLevel(logging.INFO)
for handler in sqlalchemy_logger.handlers:
    sqlalchemy_logger.removeHandler(handler)
sqlalchemy_logger.addHandler(CONSOLE_HANDLER)
sqlalchemy_logger.addHandler(FILE_HANDLER)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)


def get_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    logger.addHandler(FILE_HANDLER)
    return logger


class WerkzeugLogFilter(logging.Filter):

    def filter(self, record):
        print(record.__dict__)
        return True
