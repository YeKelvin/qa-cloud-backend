#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : parser.py
# @Time    : 2019/11/7 15:30
# @Author  : Kelvin.Ye
import traceback

from flask import request

from server.librarys.exception import ParseError
from server.librarys.request import RequestDTO
from server.utils.json_util import from_json
from server.utils.log_util import get_logger

log = get_logger(__name__)


class Argument:
    def __init__(self, name: str,
                 type: type = str,
                 default: any = None,
                 required: bool = False,
                 nullable: bool = False,
                 help: str = None):
        self.name = name  # 参数名称
        self.type = type  # 参数类型
        self.default = default  # 默认值
        self.required = required  # 参数是否必须
        self.nullable = nullable  # 参数是否可为空
        self.help = help  # 参数不符合要求时的提示语
        if not isinstance(self.name, str):
            raise TypeError('Argument name must be string')

    def parse(self, has_key, value):
        """解析 HTTP参数

        Args:
            has_key:    key是否存在
            value:      keyValue

        Returns:        HTTP参数值

        """
        # 请求中不存在该参数
        if not has_key:
            if self.required and self.default is None:
                # 若该参数必须且没有定义默认值则抛异常
                raise ParseError(self.help or f'Required Error: {self.name} is required')
            else:
                # 返回默认值
                return self.default

        # 请求中存在该参数，但值为空
        if not value:
            if self.default:
                # 返回默认值
                return self.default
            elif not self.nullable and self.required:
                # 若该参数必须、不能为空且没有定义默认值则抛异常
                raise ParseError(self.help or f'Value Error: {self.name} must not be null')
            else:
                # 若该参数可为空时，返回None
                return None

        # 类型转换
        try:
            if self.type == int:
                value = self.type(value)
            elif self.type == bool:
                assert str(value).lower() in ['true', 'false']
                value = str(value).lower() == 'true'
            elif self.type == dict or self.type == list:
                value = from_json(value)
        except (ValueError, AssertionError):
            raise ParseError(self.help or f'Type Error: {self.name} type must be {self.type}')

        return value


class BaseParser:
    def __init__(self, *args):
        self.args: [Argument] = []
        for arg in args:
            if not isinstance(arg, Argument):
                raise TypeError(f'{arg} is not instance of Argument class')
            self.args.append(arg)

    def _get(self, key):
        """通过 keyName获取 key是否存在和 keyValue的 tuple

        Args:
            key:    键名

        Returns:    (bool, obj)

        """
        raise NotImplementedError

    def _init(self, data):
        """把 HTTP请求参数转换为 Json对象
        """
        raise NotImplementedError

    def parse(self, data=None) -> RequestDTO:
        """解析 HTTP请求参数
        """
        request_dto = RequestDTO()
        try:
            self._init(data)
            for arg in self.args:
                request_dto.attr[arg.name] = arg.parse(*self._get(arg.name))
        except ParseError as err:
            request_dto.error = err.message
        except Exception as ex:
            request_dto.error = ex
            log.error(traceback.format_exc())
        return request_dto


class JsonParser(BaseParser):
    def __init__(self, *args):
        super().__init__(*args)
        self.__data = None

    def _get(self, key):
        return key in self.__data, self.__data.get(key)

    def _init(self, data):
        if not data:
            if request.is_json:
                self.__data = request.json
            else:
                self.__data = request.values.to_dict()
        else:
            if isinstance(data, str):
                self.__data = from_json(data)
            elif isinstance(data, dict):
                self.__data = data
            else:
                raise ParseError('Invalid data type for parse')
