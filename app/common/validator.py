#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : validator.py
# @Time    : 2019/11/21 15:04
# @Author  : Kelvin.Ye
import enum
from app.common.exceptions import ErrorCode
from app.common.exceptions import ServiceError


def check_is_blank(obj: any, error_msg: str = 'validation failed', error: ErrorCode = None) -> None:
    """检查obj对象是否为空，不为空则抛异常"""
    if obj:
        raise ServiceError(error_msg, error)


def check_is_not_blank(obj: any, error_msg: str = 'validation failed', error: ErrorCode = None) -> None:
    """检查obj对象是否不为空，为空则抛异常"""
    if not obj:
        raise ServiceError(error_msg, error)


def check_is_in_enum(string: str, enumeration: enum, error_msg: str = 'validation failed', error: ErrorCode = None):
    """校验枚举"""
    if string not in enumeration.__members__:
        raise ServiceError(error_msg, error)
