#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_util.py
# @Time    : 2019/11/7 10:04
# @Author  : Kelvin.Ye
import orjson
from jsonpath import jsonpath


def to_json(obj):
    """序列化
    """
    return orjson.dumps(obj)


def from_json(json_text):
    """反序列化
    """
    return orjson.loads(json_text)


def extract_json(json_text: str, json_path: str):
    """根据 JsonPath提取字段值
    """
    result_list = jsonpath(from_json(json_text), json_path)
    if len(result_list) == 1:
        return result_list[0]
    return result_list
