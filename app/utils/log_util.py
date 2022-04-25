#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/11/7 10:12
# @Author  : Kelvin.Ye
import logging
import multiprocessing
import threading
from datetime import datetime
from datetime import timezone
from logging.config import dictConfig
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from logging.handlers import TimedRotatingFileHandler

import flask

from app import config as CONFIG


logging_record_factory = logging.getLogRecordFactory()


def app_record_factory(*args, **kwargs):
    record = logging_record_factory(*args, **kwargs)
    record.traceId = 'unknown'
    return record


logging.setLogRecordFactory(app_record_factory)


# 日志格式
LOG_FORMAT = (
    '[%(asctime)s][%(levelname)s][%(threadName)s][%(name)s.%(funcName)s %(lineno)d][traceId:%(traceId)s] %(message)s'
)
FORMATTER = logging.Formatter(LOG_FORMAT)
# 日志级别
LEVEL = CONFIG.LOG_LEVEL
# 日志文件名称
LOG_FILE_NAME = CONFIG.LOG_FILE


# 控制台 Handler
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 文件滚动日志（进程不安全）
FILE_HANDLER = TimedRotatingFileHandler(LOG_FILE_NAME, when='D', interval=1, backupCount=30, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)
FILE_HANDLER.namer = lambda name: name.replace('.log', '') + '.log'

# 队列 Handler
QUEUE = multiprocessing.Queue(-1)
QUEUE_HANDLER = QueueHandler(QUEUE)
QUEUE_LISTENER = QueueListener(QUEUE, FILE_HANDLER, respect_handler_level=True)
QUEUE_LISTENER.start()


# logger全局配置
dictConfig({
    'version': 1,
    # 'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': LOG_FORMAT
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        },
        'queue': {
            'class': 'logging.handlers.QueueHandler',
            'queue': QUEUE_HANDLER,
        }
    },
    'root': {
        'propagate': False,
        'level': LEVEL,
        'handlers': ['console', 'queue']
    }
})


# werkzeug 日志配置
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False
werkzeug_logger.setLevel(logging.INFO)
for handler in werkzeug_logger.handlers:
    werkzeug_logger.removeHandler(handler)
werkzeug_logger.addHandler(CONSOLE_HANDLER)
werkzeug_logger.addHandler(QUEUE_HANDLER)


# sqlalchemy 日志配置
sqlalchemy_logger = logging.getLogger('sqlalchemy')
sqlalchemy_logger.propagate = False
sqlalchemy_logger.setLevel(logging.INFO)
for handler in sqlalchemy_logger.handlers:
    sqlalchemy_logger.removeHandler(handler)
sqlalchemy_logger.addHandler(CONSOLE_HANDLER)
sqlalchemy_logger.addHandler(QUEUE_HANDLER)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)


class ContextFilter(logging.Filter):

    traceId = 'unknown'

    def filter(self, record):
        if flask.has_app_context():
            trace_id = getattr(flask.g, 'trace_id', None)
            if not trace_id:
                trace_id = (
                    f'{threading.current_thread().ident}'
                    f'{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")}'
                )
                flask.g.trace_id = trace_id
            record.traceId = trace_id
        else:
            record.traceId = "unknown"

        return True


CONTEXT_FILTER = ContextFilter()


def get_logger(name, level=LEVEL) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    logger.addFilter(CONTEXT_FILTER)
    logger.addHandler(CONSOLE_HANDLER)
    logger.addHandler(QUEUE_HANDLER)
    return logger
