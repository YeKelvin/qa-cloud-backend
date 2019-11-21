#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : object_util.py
# @Time    : 2019/11/7 15:56
# @Author  : Kelvin.Ye


def is_empty(obj: any):
    """判断对象是否为空

    在Python中，None、空列表[]、空字典{}、空元组()、0等一系列代表空和无的对象会被转换成False。
    除此之外的其它对象都会被转化成True。

    Args:
        obj:对象

    Returns:为空返回True，非空返回False

    """
    return not obj


def is_not_empty(obj: any):
    """判断对象是否非空

    在Python中，None、空列表[]、空字典{}、空元组()、0等一系列代表空和无的对象会被转换成False。
    除此之外的其它对象都会被转化成True。

    Args:
        obj: 对象

    Returns:为空返回False，非空返回True

    """
    return bool(obj)
