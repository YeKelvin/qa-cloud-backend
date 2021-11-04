#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enums.py
# @Time    : 2020/10/30 14:49
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


class BaseEnum(Enum):

    def __eq__(self, other):
        """改造 Enum 比较函数，比较对象为 str 时，自动改为 'str' == enum.value """
        if isinstance(other, str):
            return self.value == other
        else:
            return super().__eq__(other)


@unique
class State(Enum):
    """
    状态间有迁移关系；
    用来描述过程的某个阶段，比如：进行中/已发送；处理完成后“进行中”就变成“已发送”了。
    """
    ...


@unique
class Status(Enum):
    """
    状态码没有互相迁移关系；
    用来描述操作的结果，比如：成功/失败。表示一个终结状态。
    """
    ...


@unique
class HttpStatus(Enum):
    # 1xx（临时响应），表示临时响应并需要请求者继续执行操作的状态代码。
    CODE_100 = 100  # 继续
    CODE_101 = 101  # 切换协议

    # 2xx（成功），表示成功处理了请求的状态代码。
    CODE_200 = 200  # 成功
    CODE_201 = 201  # 已创建
    CODE_202 = 202  # 已接受
    CODE_203 = 203  # 非授权信息
    CODE_204 = 204  # 无内容
    CODE_205 = 205  # 重置内容
    CODE_206 = 206  # 部分内容

    # 3xx（重定向），表示要完成请求，需要进一步操作。
    CODE_300 = 300  # 多种选择
    CODE_301 = 301  # 永久移动
    CODE_302 = 302  # 临时移动
    CODE_303 = 303  # 查看其他位置
    CODE_304 = 304  # 未修改
    CODE_305 = 305  # 使用代理
    CODE_307 = 307  # 临时重定向

    # 4xx（请求错误），表示请求可能出错，妨碍了服务器的处理。
    CODE_400 = 400  # 错误请求
    CODE_401 = 401  # 未授权
    CODE_403 = 403  # 禁止
    CODE_404 = 404  # 未找到
    CODE_405 = 405  # 方法禁用
    CODE_406 = 406  # 不接受
    CODE_407 = 407  # 需要代理授权
    CODE_408 = 408  # 请求超时
    CODE_409 = 409  # 冲突
    CODE_410 = 410  # 已删除
    CODE_411 = 411  # 需要有效长度
    CODE_412 = 412  # 未满足前提条件
    CODE_413 = 413  # 请求实体过大
    CODE_414 = 414  # 请求的URI过长
    CODE_415 = 415  # 不支持的媒体类型
    CODE_416 = 416  # 请求范围不符合要求
    CODE_417 = 417  # 未满足期望值
    CODE_428 = 428  # 要求先决条件
    CODE_429 = 429  # 太多请求
    CODE_431 = 431  # 请求头字段太大

    # 5xx（服务器错误），表示服务器在尝试处理请求时发生内部错误。
    CODE_500 = 500  # 服务器内部错误
    CODE_501 = 501  # 尚未实施
    CODE_502 = 502  # 错误网关
    CODE_503 = 503  # 服务不可用
    CODE_504 = 504  # 网关超时
    CODE_505 = 505  # HTTP版本不受支持
    CODE_511 = 511  # 要求网络认证
