#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : parser.py
# @Time    : 2019/11/7 15:30
# @Author  : Kelvin.Ye
import traceback
from enum import Enum
from typing import List
from typing import Tuple

from flask import request

from app.common.exceptions import ParseError
from app.common.request import RequestDTO
from app.common.request import transform
from app.utils.json_util import from_json
from app.utils.log_util import get_logger


log = get_logger(__name__)


class Argument:

    def __init__(
        self,
        name: str,
        type: type = str,
        default: any = None,
        required: bool = False,
        nullable: bool = False,
        min: int = None,
        max: int = None,
        enum: Enum = None,
        help: str = None
    ):
        self.name = name            # 参数名称
        self.type = type            # 参数类型
        self.default = default      # 参数默认值
        self.required = required    # 参数是否要求必传
        self.nullable = nullable    # 参数是否允许为空
        self.min = min              # 参数允许的最小值或最小长度 TODO:
        self.max = max              # 参数允许的最大值或最大长度 TODO:
        self.enum = enum            # 参数枚举校验
        self.help = help            # 参数不符合要求时的提示语

        if not isinstance(self.name, str):
            raise TypeError('argument name must be string')

    def parse(self, has_key, value):
        """解析HTTP参数

        Args:
            has_key:    key是否存在
            value:      keyValue

        Returns:        HTTP参数值

        """
        # 请求中不存在该参数
        if not has_key:
            if self.required and self.default is None:
                # 若该参数必须且没有定义默认值则抛异常
                raise ParseError(self.help or f'required error: {self.name} is required')
            else:
                # 返回默认值
                return self.default

        # 类型转换
        try:
            if self.type == int:
                value = self.type(value)
            elif self.type == bool:
                assert str(value).lower() in ['true', 'false']
                value = str(value).lower() == 'true'
            elif self.type == list:
                if not isinstance(value, list):
                    value = from_json(value)
                value = transform(value)
            elif self.type == dict:
                if not isinstance(value, dict):
                    value = from_json(value)
                value = transform(value)
        except (ValueError, AssertionError):
            raise ParseError(self.help or f'type error: {self.name} type must be {self.type}')

        # 请求中存在该参数，但值为空
        if not value:
            if self.default:
                # 返回默认值
                return self.default
            elif not self.nullable and self.required:
                # 若该参数必须、不能为空且没有定义默认值则抛异常
                raise ParseError(self.help or f'value error: {self.name} must not be null')
            else:
                # 若该参数可为空时，返回None
                return None

        # 值不为空时开始各种校验
        else:
            # 枚举校验
            if self.enum:
                if value not in self.enum.__members__:
                    # 参数值不在枚举中则抛异常
                    raise ParseError(self.help or f'value error: {self.name} invalid enumeration')

        return value


class JsonParser:

    def __init__(self, *args):
        self.data = None
        self.args: List[Argument] = []
        for arg in args:
            if not isinstance(arg, Argument):
                raise TypeError(f'{arg} is not instance of Argument class')
            self.args.append(arg)

    def get(self, key) -> Tuple[bool, any]:
        """通过key获取value"""
        return key in self.data, self.data.get(key)

    def initialize(self, data) -> None:
        """把HTTP请求参数转换为Json对象"""
        if not data:
            if request.is_json:
                self.data = request.json
            else:
                self.data = request.values.to_dict()
        else:
            if isinstance(data, str):
                self.data = from_json(data)
            elif isinstance(data, dict):
                self.data = data
            else:
                raise ParseError('invalid data type for parse')

    def parse(self, data=None) -> RequestDTO:
        """解析HTTP请求参数"""
        dto = RequestDTO(dict)
        try:
            if not self.args:
                raise ParseError('arguments are not allowed to be empty')
            self.initialize(data)
            for arg in self.args:
                dto[arg.name] = arg.parse(*self.get(arg.name))
        except ParseError as err:
            dto.__error__ = err.message
        except Exception:
            dto.__error__ = '内部错误'
            log.error(traceback.format_exc())
        return dto


class ListParser:

    def __init__(self):
        self.data = None

    def initialize(self, data) -> None:
        if not data:
            if request.is_json:
                self.data = request.json
            elif isinstance(data, str):
                self.data = from_json(data)
            else:
                raise ParseError('invalid data type for parse')
        else:
            if isinstance(data, str):
                self.data = from_json(data)
            elif isinstance(data, list):
                self.data = data
            else:
                raise ParseError('invalid data type for parse')

    def parse(self, data=None) -> RequestDTO:
        """解析HTTP请求参数"""
        dto = RequestDTO(list)
        try:

            self.initialize(data)
            dto.list = transform(self.data)
        except ParseError as err:
            dto.__error__ = err.message
        except Exception:
            dto.__error__ = '内部错误'
            log.error(traceback.format_exc())
        return dto
