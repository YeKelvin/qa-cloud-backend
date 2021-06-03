#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : validator.py
# @Time    : 2019/11/21 15:04
# @Author  : Kelvin.Ye
from app.common.exceptions import ErrorCode
from app.common.exceptions import ServiceError


def check_is_blank(obj: any, errorMsg: str = 'verify error', error: ErrorCode = None) -> None:
    """检查obj对象是否为空，不为空则抛异常

    :param obj:         对象
    :param errorMsg:    错误提示
    :param error:       错误枚举
    :return:            None
    :except:            ServiceError
    """
    if obj:
        raise ServiceError(errorMsg, error)


def check_is_not_blank(obj: any, errorMsg: str = 'verify error', error: ErrorCode = None) -> None:
    """检查obj对象是否不为空，为空则抛异常

    :param obj:         对象
    :param errorMsg:    错误提示
    :param error:       错误枚举
    :return:            None
    :except:            ServiceError
    """
    if not obj:
        raise ServiceError(errorMsg, error)
