#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : classpro
# @Time    : 2020/1/14 10:50
# @Author  : Kelvin.Ye
from app.utils.log_util import get_logger

log = get_logger(__name__)


class __ClassProperty(property):
    """类属性装饰器
    """

    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


classproperty = __ClassProperty
