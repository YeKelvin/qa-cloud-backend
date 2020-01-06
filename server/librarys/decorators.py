#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : decorators.py
# @Time    : 2019/11/7 15:41
# @Author  : Kelvin.Ye
import traceback
from datetime import datetime
from functools import wraps

from flask import request, g

from server.librarys.exception import ServiceError, ErrorCode
from server.librarys.request import RequestDTO
from server.librarys.response import http_response, ResponseDTO
from server.user.model import TUserRoleRel, TRolePermissionRel, TPermission
from server.utils.log_util import get_logger
from server.utils.time_util import current_timestamp_as_ms

log = get_logger(__name__)


def http_service(func):
    """service层装饰器，主要用于记录日志和捕获异常
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        req: RequestDTO = (args[0] if args else None) or kwargs.get('req', RequestDTO())
        # 记录开始时间
        starttime = current_timestamp_as_ms()
        log.info(
            f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
            f'header:[ {dict(request.headers.to_list("utf-8"))} ] request:[ {req.attr} ]'
        )
        res = None
        try:
            # 判断 request参数解析是否有异常
            if req.error is None:
                # 函数调用
                result = func(*args, **kwargs)
                res = ResponseDTO(result)
                log.info(
                    f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                    f'result:[ {result} ]'
                )
            else:
                res = ResponseDTO(errorMsg=req.error)
        except ServiceError as err:
            # 捕获 service层的业务异常
            res = ResponseDTO(errorMsg=err.message, errorCode=err.code)
        except Exception:
            log.error(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'traceback:[ {traceback.format_exc()} ]'
            )
            res = ResponseDTO(error=ErrorCode.E500000)
        finally:
            # 计算耗时，单位毫秒
            elapsed_time = current_timestamp_as_ms() - starttime
            http_res = http_response(res)
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'header:[ {dict(http_res.headers.to_list("utf-8"))}] response:[ {res} ] '
                f'elapsed:[ {elapsed_time}ms ]'
            )
            return http_res

    return wrapper


def require_login(func):
    """登录校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = getattr(g, 'auth_token', None)
        auth_login_time = getattr(g, 'auth_login_time', None)
        user = getattr(g, 'user', None)
        # JWT解析 payload失败
        if not auth_token or not auth_login_time:
            log.debug(f'logId:[ {g.logid} ] JWT解析 payload失败')
            return __auth_fail_response(ErrorCode.E401001)

        # 查询 user失败或 user不存在
        if not user:
            log.debug(f'logId:[ {g.logid} ] 查询 user失败或 user不存在')
            return __auth_fail_response(ErrorCode.E401001)

        # user已主动登出系统，需要重新登录
        if not user.access_token:
            log.debug(f'logId:[ {g.logid} ] user已主动登出系统，需要重新登录')
            return __auth_fail_response(ErrorCode.E401001)

        # user状态异常
        if user.state != 'NORMAL':
            log.debug(f'logId:[ {g.logid} ] user.state:[ {user.state} ] user状态异常')
            return __auth_fail_response(ErrorCode.E401001)

        # user的 access_token已更变，不能使用旧 token认证
        if auth_token != user.access_token:
            log.debug(f'logId:[ {g.logid} ] user的 access_token已更变，不能使用旧 token认证')
            return __auth_fail_response(ErrorCode.E401001)

        # user 中的最后成功登录时间和 token中的登录时间不一致
        if datetime.fromtimestamp(auth_login_time) != user.last_success_time:
            log.debug(
                f'logId:[ {g.logid} ] '
                f'auth_login_time:[ {datetime.fromtimestamp(auth_login_time)} ]'
                f'user.last_success_time:[ {user.last_success_time} ] '
                f'user中的最后成功登录时间和 token中的登录时间不一致 '
            )
            return __auth_fail_response(ErrorCode.E401001)

        g.operator = user.username
        return func(*args, **kwargs)

    return wrapper


def require_permission(func):
    """权限校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(g, 'user', None)
        if not user:
            log.debug(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'获取 flask.g.user失败'
            )
            return __auth_fail_response(ErrorCode.E401002)

        user_role = TUserRoleRel.query.filter_by(user_no=user.user_no).first()
        if not user_role:
            log.debug(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'username:[ {user.username} ] 查询用户角色失败'
            )
            return __auth_fail_response(ErrorCode.E401002)

        role_permission_rels = TRolePermissionRel.query.filter_by(role_no=user_role.role_no).all()
        if not role_permission_rels:
            log.debug(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'username:[ {user.username} ] 查询角色权限失败'
            )
            return __auth_fail_response(ErrorCode.E401002)

        for role_permission_rel in role_permission_rels:
            permission = TPermission.query.filter_by(permission_no=role_permission_rel.permission_no).first()
            if not permission:
                log.debug(
                    f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                    f'查询权限信息失败'
                )
                return __auth_fail_response(ErrorCode.E401002)

            # 校验 用户是否有该请求方法和请求路径的权限
            if request.method == permission.method and request.path == permission.endpoint:
                return func(*args, **kwargs)

        # 权限校验失败
        log.debug(f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] 用户无该请求的方法或路径的权限')
        return __auth_fail_response(ErrorCode.E401002)

    return wrapper


def __auth_fail_response(error: ErrorCode):
    user = getattr(g, 'user', None)
    log.info(
        f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
        f'header:[ {dict(request.headers.to_list("utf-8"))} ] '
        f'username:[ {user.username if user else None} ] user.state:[ {user.state if user else None} ]'
    )
    res = ResponseDTO(error=error)
    http_res = http_response(res)
    log.info(
        f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
        f'header:[ {dict(http_res.headers.to_list("utf-8"))}] response:[ {res} ]'
    )
    return http_res
