#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : request.py
# @Time    : 2019/11/13 16:26
# @Author  : Kelvin.Ye


class AttributeDict(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)

    # def __missing__(self, key):
    #     return


class RequestDTO:
    """请求对象"""
    def __init__(self, data_type=dict) -> None:
        super().__init__()
        self.__type__ = data_type
        self.__attrs__ = {}
        self.__list__ = None
        self.__error__ = None

    def __setattr__(self, key, value):
        self.__attrs__.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__attrs__.__getitem__(item)

    def __delattr__(self, item):
        self.__attrs__.__delitem__(item)


def transform(value: list or dict):
    """将dict或list对象转换为AttributeDict对象"""
    if isinstance(value, list):
        attrs = []
        for item in value:
            if isinstance(item, dict) or isinstance(item, list):
                attrs.append(transform(item))
            else:
                attrs.append(item)
        return attrs
    if isinstance(value, dict):
        attrs = {}
        for key, val in value.items():
            if isinstance(val, dict) or isinstance(val, list):
                attrs[key] = transform(val)
            else:
                attrs[key] = val
        return AttributeDict(attrs)
