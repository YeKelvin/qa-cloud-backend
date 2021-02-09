#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/11/7 10:12
# @Author  : Kelvin.Ye
import logging
# from logging.config import dictConfig

from server.common.utils import config

LOG_FORMAT = '[%(asctime)s][%(levelname)s][%(threadName)s][%(lineno)d][%(name)s.%(funcName)s] %(message)s'

"""
dictConfig({
    'version': 1,
    'root': {
        # handler的level会覆盖掉这里的level
        'level': config.get('log', 'level'),
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
"""

# 日志级别
LEVEL = config.get('log', 'level')

# 日志输出格式
FORMATTER = logging.Formatter(LOG_FORMAT)

# 输出到控制台
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 写入日志文件
LOG_FILE_NAME = config.get('log', 'name')
FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    logger.addHandler(FILE_HANDLER)
    return logger
