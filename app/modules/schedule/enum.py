#!/usr/bin/ python3
# @File    : enum.py
# @Time    : 2022/5/13 14:48
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class JobState(Enum):
    # 待开始
    PENDING = 'PENDING'
    # 运行中
    RUNNING = 'RUNNING'
    # 已暂停
    PAUSED = 'PAUSED'
    # 已关闭
    CLOSED = 'CLOSED'


@unique
class JobType(Enum):
    # 测试计划
    TESTPLAN = 'TESTPLAN'
    # 测试集合
    COLLECTION = 'COLLECTION'
    # 测试用例
    TESTCASE = 'TESTCASE'


@unique
class TriggerType(Enum):
    # 固定时间
    DATE = 'DATE'
    # CRON间隔
    CRON = 'CRON'


@unique
class JobEvents(Enum):
    # 添加作业
    ADD = 'ADD'
    # 修改作业
    MODIFY = 'MODIFY'
    # 执行作业
    EXECUTE = 'EXECUTE'
    # 暂停作业
    PAUSE = 'PAUSE'
    # 恢复作业
    RESUME = 'RESUME'
    # 关闭作业
    CLOSE = 'CLOSE'
