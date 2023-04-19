#!/usr/bin/ python3
# @File    : request.py
# @Time    : 2019/11/13 16:26
# @Author  : Kelvin.Ye
from typing import Iterable
from typing import Type


class AttributeDict(dict):

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        try:
            value = self.__getitem__(key)
            if isinstance(value, dict) and not isinstance(value, AttributeDict):
                value = AttributeDict(value)
            return value
        except KeyError as e:
            raise AttributeError(key) from e

    def __delattr__(self, key):
        self.__delitem__(key)

    # def __missing__(self, key):
    #     return


class AttributeList(list):

    def __init__(self, iterable: Iterable = None):
        super().__init__()
        if iterable:
            for item in iterable:
                self.append(transform(item))


class RequestDTO:
    """请求对象"""

    BUILT_IN = ['__type__', '__attrs__', '__error__']

    def __init__(self, data_type: Type = dict) -> None:
        self.__type__ = data_type
        self.__attrs__ = {}
        self.__error__ = None

    def __setattr__(self, key, value):
        if key in RequestDTO.BUILT_IN:
            self.__dict__[key] = value
        else:
            self.__attrs__.__setitem__(key, value)

    def __getattr__(self, item):
        """获取不存在的属性时调用"""
        return self.__attrs__.__getitem__(item)

    def __getitem__(self, item):
        return self.__attrs__.__getitem__(item)

    def __setitem__(self, key, value):
        self.__attrs__.__setitem__(key, value)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.__type__ == dict:
            return self.__attrs__.__str__()
        if self.__type__ == list:
            return self.list.__str__()
        if self.__type__ == str:
            return self.str.__str__()
        if self.__type__ == bool:
            return self.bool.__str__()
        if self.__type__ == int:
            return self.int.__str__()
        if self.__type__ == float:
            return self.float.__str__()


def transform(value: list or dict):
    """将 dict 或 list 对象转换为 AttributeDict 对象"""
    if isinstance(value, list):
        attrs = []
        for item in value:
            if isinstance(item, (dict, list)):
                attrs.append(transform(item))
            else:
                attrs.append(item)
        return attrs
    elif isinstance(value, dict):
        attrs = {key: transform(val) if isinstance(val, (dict, list)) else val for key, val in value.items()}

        return AttributeDict(attrs)
    else:
        return value
