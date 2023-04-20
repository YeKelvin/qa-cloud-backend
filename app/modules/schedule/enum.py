#!/usr/bin/ python3
# @File    : enum.py
# @Time    : 2022/5/13 14:48
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class JobState(Enum):
    # 正常
    NORMAL = 'NORMAL'
    # 已暂停
    PAUSED = 'PAUSED'
    # 已关闭
    CLOSED = 'CLOSED'


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
    # 固定间隔
    INTERVAL = 'INTERVAL'
    # CRON间隔
    CRON = 'CRON'


@unique
class OperationType(Enum):
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


@unique
class ChangeType(Enum):
    JOB_TYPE = 'JOB_TYPE'
    JOB_ARGS = 'JOB_ARGS'
    TRIGGER_TYPE = 'TRIGGER_TYPE'
    TRIGGER_ARGS = 'TRIGGER_ARGS'
