#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time_util.py
# @Time    : 2019/11/7 10:13
# @Author  : Kelvin.Ye
import time
from datetime import datetime


def current_time_as_str() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def current_time_as_ms() -> int:
    """获取毫秒级时间戳，用于计算毫秒级耗时
    """
    return int(time.time() * 1000)


def current_time_as_s() -> int:
    """获取秒级时间戳，用于计算秒级耗时
    """
    return int(time.time())


def seconds_convert_to_hms(seconds: int) -> str:
    """秒数转换为时分秒
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%02dh:%02dm:%02ds' % (h, m, s)


def sleep(secs: float) -> None:
    """睡眠等待
    """
    time.sleep(secs)
