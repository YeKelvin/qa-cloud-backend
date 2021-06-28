#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enum.py
# @Time    : 2020/7/3 15:07
# @Author  : Kelvin.Ye
from enum import Enum


class WorkspaceType(Enum):
    # 公共
    PUBLIC = 'PUBLIC'


class WorkspaceScope(Enum):
    # 个人
    PERSONAL = 'PERSONAL'

    # 公共
    PUBLIC = 'PUBLIC'

    # 项目
    PROJECT = 'PROJECT'

    # 团队
    TEAM = 'TEAM'
