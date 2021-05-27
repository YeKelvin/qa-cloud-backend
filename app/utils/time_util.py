#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time_util.py
# @Time    : 2019/11/7 10:13
# @Author  : Kelvin.Ye
import time
from datetime import datetime


STRFTIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def strftime(format: str = STRFTIME_FORMAT) -> str:
    """获取当前时间并格式化为时间字符串

    :param format:  时间格式
    :return:        str
    """
    return datetime.now().strftime(format)


def timestamp_as_s() -> int:
    """获取秒级时间戳
    """
    return int(time.time())


def timestamp_as_ms() -> int:
    """获取毫秒级时间戳
    """
    return int(time.time() * 1000)


def timestamp_as_micro_s() -> int:
    """获取微秒级时间戳
    """
    return int(round(time.time() * 1000000))


def timestamp_to_strftime(format: str = STRFTIME_FORMAT, timestamp: float = 0):
    """时间戳转时间字符串

    :param format:      时间格式
    :param timestamp:   时间戳
    :return:            float
    """
    return time.strftime(format, time.localtime(timestamp))


def strftime_to_timestamp_as_ms(strftime: str, format: str = STRFTIME_FORMAT):
    """时间字符串转毫秒级时间戳

    :param strftime:    时间字符串
    :param format:      时间格式
    :return:            float
    """
    return int(time.mktime(time.strptime(strftime, format)) * 1000)


def change_strftime_format(strftime: str, old_format: str, new_format: str = STRFTIME_FORMAT):
    """更改时间字符串的格式

    :param strftime:    时间字符串
    :param old_format:  旧格式
    :param new_format:  新格式
    :return:            str
    """
    return datetime.strptime(strftime, old_format).strftime(new_format)


def seconds_to_h_m_s(seconds: int) -> str:
    """秒数转换为时分秒
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%02dh:%02dm:%02ds' % (h, m, s)


def sleep(secs: float) -> None:
    """睡眠等待
    """
    time.sleep(secs)
