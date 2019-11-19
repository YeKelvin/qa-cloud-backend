#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : request.py
# @Time    : 2019/11/13 16:26
# @Author  : Kelvin.Ye


class RequestDTO:
    """请求对象
    """

    def __init__(self):
        self.attr = AttrDict()
        self.error = None


class AttrDict(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)
