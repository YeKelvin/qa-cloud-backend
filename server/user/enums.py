#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enums
# @Time    : 2020/7/3 15:07
# @Author  : Kelvin.Ye
from enum import Enum


class UserState(Enum):
    ENABLE = 'ENABLE'
    DISABLE = 'DISABLE'


class RoleState(Enum):
    ENABLE = 'ENABLE'
    DISABLE = 'DISABLE'


class PermissionState(Enum):
    ENABLE = 'ENABLE'
    DISABLE = 'DISABLE'
