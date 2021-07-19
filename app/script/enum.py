#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enum.py
# @Time    : 2020/7/3 15:23
# @Author  : Kelvin.Ye
from enum import unique, Enum


@unique
class ElementType(Enum):
    # 测试集合
    COLLECTION = 'COLLECTION'

    # 测试组
    GROUP = 'GROUP'

    # 取样器
    SAMPLER = 'SAMPLER'

    # 配置器
    CONFIG = 'CONFIG'

    # 逻辑控制器
    CONTROL = 'CONTROL'

    # 时间控制器
    TIMER = 'TIMER'

    # 前置处理器
    PRE_PROCESSOR = 'PRE_PROCESSOR'

    # 后置处理器
    POST_PROCESSOR = 'POST_PROCESSOR'

    # 断言器
    ASSERTION = 'ASSERTION'

    # 监听器
    LISTENER = 'LISTENER'


@unique
class ElementClass(Enum):
    # 测试集合
    TEST_COLLECTION = 'TEST_COLLECTION'

    # 测试组
    TEST_GROUP = 'TEST_GROUP'

    # HTTP取样器
    HTTP_SAMPLER = 'HTTP_SAMPLER'

    # Python取样器
    PYTHON_SAMPLER = 'PYTHON_SAMPLER'

    # SQL取样器
    SQL_SAMPLER = 'SQL_SAMPLER'

    # HTTP头部配置器
    HTTP_HEADER_MANAGER = 'HTTP_HEADER_MANAGER'

    # 循环控制器
    LOOP_CONTROL = 'LOOP_CONTROL'

    # if控制器
    IF_CONTROL = 'IF_CONTROL'

    # Python前置处理器
    PYTHON_PRE_PROCESSOR = 'PYTHON_PRE_PROCESSOR'

    # Python后置处理器
    PYTHON_POST_PROCESSOR = 'PYTHON_POST_PROCESSOR'

    # JsonPath提取器
    JSON_PATH_EXTRACTOR = 'JSON_PATH_EXTRACTOR'

    # Python断言器
    PYTHON_ASSERTION = 'PYTHON_ASSERTION'

    # JsonPath断言器
    JSON_PATH_ASSERTION = 'JSON_PATH_ASSERTION'


@unique
class ElementStatus(Enum):
    # 启用
    ENABLE = True

    # 禁用
    DISABLE = False


@unique
class VariableSetType(Enum):

    # 全局变量：与环境无关，与工作空间无关
    GLOBAL = 'GLOBAL'

    # 环境变量：与环境相关，与工作空间相关
    ENVIRONMENT = 'ENVIRONMENT'

    # 自定义变量：与环境无关，与工作空间相关
    CUSTOM = 'CUSTOM'
