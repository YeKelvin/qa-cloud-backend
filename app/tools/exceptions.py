#!/usr/bin/ python3
# @File    : exceptions.py
# @Time    : 2019/11/7 11:55
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class ServiceStatus(Enum):
    """业务错误码枚举

    错误码命名规范：E前缀+后三位数，后三位数从000开始递增
    +-----------------------+
    |错误码      |描述
    +-----------------------+
    |200        |成功
    |201        |已存在
    |401        |未授权
    |403        |禁止
    |404        |不存在
    |405        |状态异常
    |415        |格式错误
    |500        |内部错误
    |600        |业务错误
    +-----------------------+
    """
    # 2XX
    CODE_200 = {'code':200, 'message':'成功'}
    CODE_201 = {'code':200, 'message':'已存在'}

    # 4XX
    CODE_401 = {'code':401, 'message':'未登录'}
    CODE_403 = {'code':403, 'message':'无权限'}
    CODE_404 = {'code':404, 'message':'不存在'}
    CODE_405 = {'code':405, 'message':'状态异常'}
    CODE_415 = {'code':405, 'message':'格式错误'}

    # 5XX
    CODE_500 = {'code':500, 'message':'内部错误'}

    # 6XX
    CODE_600 = {'code':600, 'message':'业务错误'}

    @property
    def CODE(self):
        return self.value.get('code')

    @property
    def MSG(self):
        return self.value.get('message')


class ServiceError(Exception):
    """业务异常类"""

    def __init__(self, *, msg: str = None, code: str = None, error: ServiceStatus = None):
        super().__init__(self)
        if error is None:
            self.code = code or ServiceStatus.CODE_600.CODE
            self.message = msg or ServiceStatus.CODE_600.MSG
        else:
            self.code = error.value.get('code')
            self.message = error.value.get('msg')


class ParseError(Exception):
    """请求参数解析异常类"""

    def __init__(self, msg=None):
        self.message = msg


class TestplanInterruptError(Exception):
    ...
