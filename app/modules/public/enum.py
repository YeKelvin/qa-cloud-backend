#!/usr/bin/ python3
# @File    : enum.py
# @Time    : 2020/7/3 15:07
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class WorkspaceScope(Enum):

    # 个人空间，每个用户注册后都有个人空间
    PRIVATE = 'PRIVATE'

    # 团队空间，需要添加用户关联，在空间下的用户才能使用空间
    PROTECTED = 'PROTECTED'

    # 公共空间，不需要添加用户关联，所有用户都可以使用
    PUBLIC = 'PUBLIC'


@unique
class RobotState(Enum):
    # 启用
    ENABLE = 'ENABLE'
    # 禁用
    DISABLE = 'DISABLE'


@unique
class RobotType(Enum):
    # 企业微信
    WECOM = 'WECOM'
    # 钉钉
    DINGTALK = 'DINGTALK'
