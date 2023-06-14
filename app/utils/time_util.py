#!/usr/bin/ python3
# @File    : time_util.py
# @Time    : 2019/11/7 10:13
# @Author  : Kelvin.Ye
import time

from datetime import datetime
from datetime import timedelta
from datetime import timezone


TIMEFMT = '%Y-%m-%d %H:%M:%S'


def strftime(format: str = TIMEFMT) -> str:
    """获取当前时间并格式化为时间字符串

    :param format:  时间格式
    :return:        str
    """
    return datetime.now().strftime(format)


def timestamp_now() -> float:
    """获取时间戳（从UTC时间 1970年1月1日 0点 到现在的秒值）"""
    return time.time()


def timestamp_to_utc8_datetime(timestmp) -> datetime:
    """时间戳转北京时间的 datetime 对象"""
    return datetime.fromtimestamp(timestmp, tz=timezone(timedelta(hours=8)))


def timestamp_as_ms() -> int:
    """获取毫秒级时间戳"""
    return int(time.time() * 1000)


def timestamp_as_micro_s() -> int:
    """获取微秒级时间戳"""
    return int(round(time.time() * 1000000))


def timestamp_to_strftime(format: str = TIMEFMT, timestamp: float = 0):
    """时间戳转时间字符串

    :param format:      时间格式
    :param timestamp:   时间戳
    :return:            float
    """
    return time.strftime(format, time.localtime(timestamp))


def strftime_to_timestamp_as_ms(strftime: str, format: str = TIMEFMT):
    """时间字符串转毫秒级时间戳

    :param strftime:    时间字符串
    :param format:      时间格式
    :return:            float
    """
    return int(time.mktime(time.strptime(strftime, format)) * 1000)


def change_strftime_format(strftime: str, old_format: str, new_format: str = TIMEFMT):
    """更改时间字符串的格式

    :param strftime:    时间字符串
    :param old_format:  旧格式
    :param new_format:  新格式
    :return:            str
    """
    return datetime.strptime(strftime, old_format).strftime(new_format)


def sleep(secs: float) -> None:
    """睡眠等待"""
    time.sleep(secs)


def datetime_now_by_utc8() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def microsecond_to_h_m_s(microsecond: int) -> str:
    """毫秒转换为时分秒"""
    if not microsecond:
        return '0ms'

    s, ms = divmod(microsecond, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h == 0:
        if m == 0:
            return '%dms' % ms if s == 0 else '%02ds+%dms' % (s, ms)
        return '%02dm:%02ds' % (m, s)

    return '%02dh:%02dm:%02ds' % (h, m, s)


def microsecond_to_m_s(microsecond: int) -> str:
    """毫秒转换为时分秒"""
    if not microsecond:
        return '0ms'

    s, ms = divmod(microsecond, 1000)
    m, s = divmod(s, 60)
    if m == 0:
        return '%dms' % ms if s == 0 else '%02ds+%dms' % (s, ms)
    return '%02dm:%02ds' % (m, s)
