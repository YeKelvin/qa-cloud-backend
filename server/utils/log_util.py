#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/11/7 10:12
# @Author  : Kelvin.Ye
import logging
import logging.config

from server.utils import config

# 日志输出格式
FORMATTER = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(threadName)s][null][%(lineno)d][%(name)s.%(funcName)s][null] %(message)s'
)

# 输出到控制台
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 写入日志文件
LOG_FILE_NAME = config.get('log', 'name')
FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME)

# 日志级别
LEVEL = config.get('log', 'level')


def get_logger(name):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    return logger
