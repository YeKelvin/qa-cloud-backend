#!/usr/bin/ python3
# @File    : log_util.py
# @Time    : 2023-04-14 15:43:04
# @Author  : Kelvin.Ye
import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """logging转loguru的handler"""
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 过滤
        if ('werkzeug' in record.name or 'sqlalchemy' in record.name or 'apscheduler' in record.name) and record.levelno < logging.INFO:
            return
        if ('httpx' in record.name or 'httpcore' in record.name) and record.levelno < logging.WARNING:
            return

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def console_formatter(record):
    name = str(record['name'])
    if 'werkzeug' in name:
        return '{message}\n'
    elif 'sqlalchemy' in name or 'apscheduler' in name:
        return '<green>[{time:%Y-%m-%d %H:%M:%S.%f}]</green> <level>[{level}] {message}</level>\n'
    else:
        traceid = '[traceid:{extra[traceid]}] ' if record['extra'].get('traceid') else ''
        return '<green>[{time:%Y-%m-%d %H:%M:%S.%f}]</green> <level>[{level}] [{module}:{function}:{line}] ' + traceid + '{message}</level>\n'


def file_formatter(record):
    name = str(record['name'])
    if 'werkzeug' in name:
        return '{message}\n'
    elif 'sqlalchemy' in name or 'apscheduler' in name:
        return '[{time:%Y-%m-%d %H:%M:%S.%f}] [{level}] {message}\n'
    else:
        traceid = '[traceid:{extra[traceid]}] ' if record['extra'].get('traceid') else ''
        return '[{time:%Y-%m-%d %H:%M:%S.%f}] [{level}] [{module}:{function}:{line}] ' + traceid + '{message}\n'
