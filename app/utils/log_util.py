#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/11/7 10:12
# @Author  : Kelvin.Ye
import logging
import multiprocessing
from logging.config import dictConfig
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from logging.handlers import TimedRotatingFileHandler

from app import config as CONFIG


# 日志格式
LOG_FORMAT = '[%(asctime)s][%(levelname)s][%(threadName)s][%(name)s.%(funcName)s %(lineno)d] %(message)s'
FORMATTER = logging.Formatter(LOG_FORMAT)
# 日志级别
LEVEL = CONFIG.LOG_LEVEL
# 日志文件名称
LOG_FILE_NAME = CONFIG.LOG_NAME


# logger全局配置
dictConfig({
    'version': 1,
    'root': {
        'propagate': False,
        'level': LEVEL,  # handler的 level 会覆盖掉这里的 level
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
            'filename': LOG_FILE_NAME
        }
    },
    'formatters': {
        'default': {
            'format': LOG_FORMAT
        }
    }
})


# 控制台 Handler
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 文件 Handler
# FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf-8')
# 文件滚动日志（线程不安全）
FILE_HANDLER = TimedRotatingFileHandler(LOG_FILE_NAME, when='MIDNIGHT', interval=1, backupCount=30, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)
FILE_HANDLER.suffix = "%Y-%m-%d_%H-%M-%S.log"

# 队列 Handler
QUEUE = multiprocessing.Queue(-1)
QUEUE_HANDLER = QueueHandler(QUEUE)
QUEUE_LISTENER = QueueListener(QUEUE, FILE_HANDLER)
QUEUE_LISTENER.start()

# werkzeug 日志配置
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False
werkzeug_logger.setLevel(logging.INFO)
for handler in werkzeug_logger.handlers:
    werkzeug_logger.removeHandler(handler)
werkzeug_logger.addHandler(CONSOLE_HANDLER)
werkzeug_logger.addHandler(FILE_HANDLER)

# sqlalchemy 日志配置
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


def get_logger(name, level=LEVEL) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(CONSOLE_HANDLER)
    # logger.addHandler(FILE_HANDLER)
    logger.addHandler(QUEUE_HANDLER)
    return logger


class WerkzeugLogFilter(logging.Filter):

    def filter(self, record):
        print(record.__dict__)
        return True
