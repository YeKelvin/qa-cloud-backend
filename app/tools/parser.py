#!/usr/bin/ python3
# @File    : parser.py
# @Time    : 2019/11/7 15:30
# @Author  : Kelvin.Ye
from enum import Enum

from flask import request
from loguru import logger

from app.tools.exceptions import ParseError
from app.tools.request import RequestDTO
from app.tools.request import transform
from app.utils.json_util import from_json


class Argument:

    def __init__(
        self,
        name: str,
        type: type = None,
        default: any = None,
        required: bool = False,
        nullable: bool = False,
        min: int = None,
        max: int = None,
        enum: type[Enum] = None,
        help: str = None
    ):
        self.name = name            # 参数名称
        self.type = type            # 参数类型
        self.default = default      # 参数默认值
        self.required = required    # 参数是否要求必传
        self.nullable = nullable    # 参数是否允许为null
        self.min = min              # 参数允许的最小值或最小长度
        self.max = max              # 参数允许的最大值或最大长度
        self.enum = enum            # 参数枚举校验
        self.help = help            # 参数不符合要求时的提示语

        if not isinstance(self.name, str):
            raise TypeError('Argument name must be string')

    def parse(self, has_key, value):
        """解析HTTP参数"""
        # 不存在该参数，返回默认值
        if not has_key:
            return self.get_required_default()

        # 存在该参数，但值为null，返回默认值
        if value is None:
            return self.get_nullable_default()

        # 类型转换
        if self.type:
            value = self.convert_type(value)

        # 数据校验
        self.validate(value)

        return value

    def get_required_default(self):
        if self.required and self.default is None:
            # 若该参数为必填项、且没有定义默认值则抛出异常
            raise ParseError(self.help or f'Required Error: {self.name} is required')
        else:
            # 返回默认值
            return self.default

    def get_nullable_default(self):
        if self.default:
            # 返回默认值
            return self.default
        elif not self.nullable and self.required:
            # 若该参数为必填项、且不能为空，且没有定义默认值则抛出异常
            raise ParseError(self.help or f'Value Error: {self.name} must not be null')
        else:
            # 若该参数可为空则返回None
            return None

    def convert_type(self, value):
        # sourcery skip: raise-from-previous-error
        try:
            # string
            if self.type == str:
                if not isinstance(value, str):
                    value = str(value)
            # int
            elif self.type == int:
                if not isinstance(value, int):
                    value = int(value)
            # float
            elif self.type == float:
                if not isinstance(value, float):
                    value = float(value)
            # bool
            elif self.type == bool:
                value = str(value).lower()
                assert value in {'true', 'false'}, '布尔值错误'
                value = value == 'true'
            # list
            elif self.type == list:
                # body传递数组
                if not isinstance(value, list):
                    value = from_json(value)
                    assert isinstance(value, list), '参数值非列表'
                # 转换为attribute对象
                value = transform(value)
            # dict
            elif self.type == dict:
                if not isinstance(value, dict):
                    value = from_json(value)
                    assert isinstance(value, dict), '参数值非字典'
                # 转换为attribute对象
                value = transform(value)
            else:
                raise TypeError('Invalid Type')
            return value
        except (TypeError, ValueError, AssertionError):
            raise ParseError(f'Type Error: {self.name} type must be {self.type}')

    def validate(self, value):
        # 枚举校验
        if self.enum and value not in self.enum.__members__:
            raise ParseError(self.help or f'Value Error: {self.name} invalid enumeration')

        # 整型最大最小值校验
        if self.type == int:
            if self.min is not None and value < self.min:
                raise ParseError(f'Value Error: {self.name} cannot be < {self.min}')
            if self.max is not None and value > self.max:
                raise ParseError(f'Value Error: {self.name} cannot be > {self.max}')

        # 字符串最大最小长度校验
        if self.type == str:
            if self.min is not None and len(value) < self.min:
                raise ParseError(f'Value Error: {self.name} length cannot be < {self.min}')
            if self.max is not None and len(value) > self.max:
                raise ParseError(f'Value Error: {self.name} length cannot be > {self.max}')


class JsonParser:

    def __init__(self, *args):
        self.data = None
        self.args: list[Argument] = args

    def get(self, key, argtype) -> tuple[bool, any]:
        """通过key获取value"""
        if request.method == 'GET' and argtype == list:
            value = request.args.getlist(key)
        else:
            value = self.data.get(key)
        # 返回是否存在key和值
        return key in self.data, value

    def initialize(self, data) -> None:
        """把HTTP请求参数转换为Json对象"""
        if not data:
            self.data = request.json if request.is_json else request.values.to_dict()
        elif isinstance(data, str):
            self.data = from_json(data)
        elif isinstance(data, dict):
            self.data = data
        else:
            raise ParseError('Invalid data type for parse')

    def parse(self, data=None) -> RequestDTO:
        """解析HTTP请求参数"""
        dto = RequestDTO(dict)
        try:
            # 校验非空
            if not self.args:
                raise ParseError('Arguments are not allowed to be empty')
            # 初始化数据
            self.initialize(data)
            # 遍历解析
            for arg in self.args:
                if not isinstance(arg, Argument):
                    raise TypeError(f'{arg} is not instance of Argument class')
                dto[arg.name] = arg.parse(*self.get(arg.name, arg.type))
        except ParseError as err:
            dto.__error__ = err.message
        except Exception as e:
            dto.__error__ = '内部错误'
            logger.exception(e)
        finally:
            return dto
