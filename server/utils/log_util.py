#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/11/7 10:12
# @Author  : Kelvin.Ye

"""
Log输出格式：
- %(name)s：             Logger的名字
- %(levelno)s：          数字形式的日志级别
- %(levelname)s：        文本形式的日志级别
- %(pathname)s：         调用日志输出函数的模块的完整路径名，可能没有
- %(filename)s：         调用日志输出函数的模块的文件名
- %(module)s：           调用日志输出函数的模块名
- %(funcName)s：         调用日志输出函数的函数名
- %(lineno)d：           调用日志输出函数的语句所在的代码行
- %(created)f：          当前时间，用UNIX标准的表示时间的浮 点数表示
- %(relativeCreated)d：  输出日志信息时的，自Logger创建以 来的毫秒数
- %(asctime)s：          字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”
- %(thread)d：           线程ID（可能没有）
- %(threadName)s：       线程名（可能没有）
- %(process)d：          进程ID（可能没有）
- %(message)s：          用户输出的消息

时间格式：
- %y    两位数的年份表示（00-99）
- %Y    四位数的年份表示（000-9999）
- %m    月份（01-12）
- %d    月内中的一天（0-31）
- %H    24小时制小时数（0-23）
- %I    12小时制小时数（01-12）
- %M    分钟数（00=59）
- %S    秒（00-59）
- %a    本地简化星期名称
- %A    本地完整星期名称
- %b    本地简化的月份名称
- %B    本地完整的月份名称
- %c    本地相应的日期表示和时间表示
- %j    年内的一天（001-366）
- %p    本地A.M.或P.M.的等价符
- %U    一年中的星期数（00-53）星期天为星期的开始
- %w    星期（0-6），星期天为星期的开始
- %W    一年中的星期数（00-53）星期一为星期的开始
- %x    本地相应的日期表示
- %X    本地相应的时间表示
- %Z    当前时区的名称
- %%    %号本身
"""

import logging

from server.utils import config

# 日志输出格式
FORMATTER = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s.%(funcName)s] %(message)s')

# 输出到控制台
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 写入日志文件
FILE_HANDLER = logging.FileHandler(config.get('log', 'name'))

# 日志级别
LEVEL = config.get('log', 'level')


def get_logger(name):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    return logger
