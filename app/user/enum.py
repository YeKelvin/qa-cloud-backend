#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


class PermissionState(Enum):
    # 启用
    ENABLE = 'ENABLE'

    # 禁用
    DISABLE = 'DISABLE'
