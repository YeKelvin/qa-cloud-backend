#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2023-04-14 15:43:04
# @Author  : Kelvin.Ye
import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
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

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
