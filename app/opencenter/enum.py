#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enum.py
# @Time    : 2023-04-17 17:26:00
# @Author  : Kelvin.Ye
from enum import Enum


class APPState(Enum):

    # 启用
    ENABLE = 'ENABLE'

    # 禁用
    DISABLE = 'DISABLE'
