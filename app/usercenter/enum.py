#!/usr/bin/ python3
# @File    : enum.py
# @Time    : 2020/7/3 15:07
# @Author  : Kelvin.Ye
from enum import Enum


class UserState(Enum):

    # 启用
    ENABLE = 'ENABLE'

    # 禁用
    DISABLE = 'DISABLE'


class RoleState(Enum):

    # 启用
    ENABLE = 'ENABLE'

    # 禁用
    DISABLE = 'DISABLE'


class GroupState(Enum):

    # 启用
    ENABLE = 'ENABLE'

    # 禁用
    DISABLE = 'DISABLE'
