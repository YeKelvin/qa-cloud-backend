#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enum.py
# @Time    : 2022/5/13 14:48
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class JobType(Enum):
    # 测试计划
    TESTPLAN = 'TESTPLAN'
    # 集合元素
    COLLECTION = 'COLLECTION'
    # 分组元素
    GROUP = 'GROUP'


@unique
class TriggerType(Enum):
    # 固定时间
    DATE = 'DATE'
    # 固定时间间隔
    INTERVAL = 'INTERVAL'
    # Cron间隔
    CRON = 'CRON'
