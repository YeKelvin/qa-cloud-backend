#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : verify
# @Time    : 2019/11/21 15:04
# @Author  : Kelvin.Ye
from server.librarys.exception import ServiceError, ErrorCode


class Verify:
    """verification
    """

    @staticmethod
    def is_empty(obj: any, errorMsg: str = 'verify error', error: ErrorCode = None) -> None:
        """验证 obj对象为空，不为空则抛异常

        :param obj:         对象
        :param errorMsg:    错误提示
        :param error:       错误枚举
        :return:            None
        :except:            ServiceError
        """
        if obj:
            raise ServiceError(errorMsg, error)

    @staticmethod
    def is_not_empty(obj: any, errorMsg: str = 'verify error', error: ErrorCode = None) -> None:
        """验证 obj对象非空，为空则抛异常

        :param obj:         对象
        :param errorMsg:    错误提示
        :param error:       错误枚举
        :return:            None
        :except:            ServiceError
        """
        if not obj:
            raise ServiceError(errorMsg, error)
