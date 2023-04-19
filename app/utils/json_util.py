#!/usr/bin/ python3
# @File    : json_util.py
# @Time    : 2019/11/7 10:04
# @Author  : Kelvin.Ye
import orjson
from jsonpath import jsonpath
from orjson import JSONDecodeError


def to_json(obj):
    """序列化"""
    try:
        return orjson.dumps(obj, option=orjson.OPT_NAIVE_UTC).decode('utf8')
    except TypeError as e:
        e.args = e.args + (f'obj:[ {obj} ]',)
        raise e


def from_json(val):
    """反序列化"""
    try:
        return orjson.loads(val)
    except JSONDecodeError as e:
        e.args = e.args + (f'value: {val}',)
        raise e


def extract_json(val: str, json_path: str):
    """根据 JsonPath提取字段值"""
    result_list = jsonpath(from_json(val), json_path)
    if len(result_list) == 1:
        return result_list[0]
    return result_list
