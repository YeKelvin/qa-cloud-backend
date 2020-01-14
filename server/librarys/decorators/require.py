#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : require
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
from datetime import datetime
from functools import wraps

from flask import request, g

from server.librarys.exception import ErrorCode
from server.librarys.helpers.global_helper import Global
from server.librarys.response import http_response, ResponseDTO
from server.user.model import TUserRoleRel, TRolePermissionRel, TPermission, TRole
from server.utils.log_util import get_logger

log = get_logger(__name__)


def require_login(func):
    """登录校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = Global.auth_token
        auth_login_time = Global.auth_login_time
        user = Global.user
        # JWT解析 payload失败
        if not auth_token or not auth_login_time:
            log.info(f'logId:[ {g.logid} ] msg:[ JWT解析 payload失败 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # 查询 user失败或 user不存在
        if not user:
            log.info(f'logId:[ {g.logid} ] msg:[ 查询 user失败或 user不存在 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # user已主动登出系统，需要重新登录
        if not user.access_token:
            log.info(f'logId:[ {g.logid} ] msg:[ user已主动登出系统，需要重新登录 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # user状态异常
        if user.state != 'NORMAL':
            log.info(f'logId:[ {g.logid} ] user.state:[ {user.state} ] msg:[ user状态异常 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # user的 access_token已更变，不能使用旧 token认证
        if auth_token != user.access_token:
            log.info(f'logId:[ {g.logid} ] msg:[ user的 access_token已更变，不能使用旧 token认证 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # user 中的最后成功登录时间和 token中的登录时间不一致
        if datetime.fromtimestamp(auth_login_time) != user.last_success_time:
            log.info(
                f'logId:[ {g.logid} ] '
                f'auth_login_time:[ {datetime.fromtimestamp(auth_login_time)} ]'
                f'user.last_success_time:[ {user.last_success_time} ] '
                f'msg:[ user中的最后成功登录时间和 token中的登录时间不一致 ]'
            )
            return __auth_fail_response(ErrorCode.E401001)

        Global.set('operator', user.username)
        return func(*args, **kwargs)

    return wrapper


def require_permission(func):
    """权限校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取登录用户
        user = Global.user
        if not user:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'msg:[ 获取 flask.g.user失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询权限信息
        permission = TPermission.query.filter_by(endpoint=request.path, method=request.method).first()
        if not permission:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'msg:[ 查询请求路由权限信息失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 判断权限状态是否已禁用
        if permission.state != 'NORMAL':
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'permissionNo:[ {permission.permission_no} ] permissionName:[ {permission.permission_name} ]'
                f'msg:[ 权限状态异常 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询用户角色
        user_role = TUserRoleRel.query.filter_by(user_no=user.user_no).first()
        if not user_role:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user.user_no} ] username:[ {user.username} ] msg:[ 查询用户角色失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询角色信息
        role = TRole.query.filter_by(role_no=user_role.role_no, state='NORMAL').first()
        if not role:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user.user_no} ] username:[ {user.username} ] roleNo:[ {user_role.role_no} ] '
                f'msg:[ 查询角色信息失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 判断权限状态是否已禁用
        if role.state != 'NORMAL':
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user.user_no} ] username:[ {user.username} ] '
                f'roleNo:[ {role.role_no} ] roleName:[ {role.role_name} ]'
                f'msg:[ 角色状态异常 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询角色权限关联关系
        role_permission_rel = TRolePermissionRel.query.filter_by(
            role_no=user_role.role_no, permission_no=permission.permission_no
        ).first()
        if not role_permission_rel:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user.user_no} ] username:[ {user.username} ] '
                f'roleNo:[ {user_role.role_no} ] permissionNo:[ {permission.permission_no} ]'
                f'msg:[ 查询角色权限关联关系失败，用户无当前请求的权限 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        return func(*args, **kwargs)

    return wrapper


def __auth_fail_response(error: ErrorCode):
    user = Global.user
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
