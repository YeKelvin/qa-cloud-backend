#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : require
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
from datetime import datetime
from functools import wraps

from flask import g
from flask import request

from app.common.exceptions import ErrorCode
from app.common.helpers.global_helper import Global
from app.common.response import http_response
from app.common.response import ResponseDTO
from app.user.models import TPermission
from app.user.models import TRole
from app.user.models import TRolePermissionRel
from app.user.models import TUser
from app.user.models import TUserAccessToken
from app.user.models import TUserPassword
from app.user.models import TUserRoleRel
from app.utils.log_util import get_logger

log = get_logger(__name__)


def require_login(func):
    """登录校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = Global.auth_token
        auth_login_time = Global.auth_login_time
        user_no = Global.user_no
        # JWT解析 payload失败
        if not auth_token or not auth_login_time:
            log.info(f'logId:[ {g.logid} ] msg:[ JWT解析 payload失败 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # 用户不存在
        user = TUser.query.filter_by(USER_NO=user_no).first()
        if not user:
            log.info(f'logId:[ {g.logid} ] msg:[ 用户不存在 ]')
            return __auth_fail_response(ErrorCode.E401001)

        user_token = TUserAccessToken.query.filter_by(USER_NO=user_no).first()
        # 用户未登录，请先登录
        if not user_token:
            log.info(f'logId:[ {g.logid} ] msg:[ 用户未登录，请先登录 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # 用户已登出系统，请重新登录
        if not user_token.ACCESS_TOKEN:
            log.info(f'logId:[ {g.logid} ] msg:[ 用户已登出系统，请重新登录 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # 用户状态异常
        if user.STATE != 'ENABLE':
            log.info(f'logId:[ {g.logid} ] user.state:[ {user.STATE} ] msg:[ 用户状态异常 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # 用户异设备登录，请重新登录
        if auth_token != user_token.ACCESS_TOKEN:
            log.info(f'logId:[ {g.logid} ] msg:[ 用户异设备登录，请重新登录 ]')
            return __auth_fail_response(ErrorCode.E401001)

        # 用户最后成功登录时间和 token中的登录时间不一致
        user_password = TUserPassword.query.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()
        if datetime.fromtimestamp(auth_login_time) != user_password.LAST_SUCCESS_TIME:
            log.info(
                f'logId:[ {g.logid} ] '
                f'auth_login_time:[ {datetime.fromtimestamp(auth_login_time)} ]'
                f'last_success_time:[ {user_password.LAST_SUCCESS_TIME} ] '
                f'msg:[ 用户最后成功登录时间和 token中的登录时间不一致 ]'
            )
            return __auth_fail_response(ErrorCode.E401001)

        Global.set('operator', user.USER_NAME)
        return func(*args, **kwargs)

    return wrapper


def require_permission(func):
    """权限校验装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取登录用户
        user_no = Global.user_no
        if not user_no:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'msg:[ 获取 flask.g.user_no失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询权限信息
        permission = TPermission.query.filter_by(ENDPOINT=request.path, METHOD=request.method).first()
        if not permission:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'msg:[ 查询请求路由权限信息失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 判断权限状态是否已禁用
        if permission.STATE != 'ENABLE':
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'permissionNo:[ {permission.PERMISSION_NO} ] permissionName:[ {permission.PERMISSION_NAME} ]'
                f'msg:[ 权限状态异常 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询用户角色
        user_role = TUserRoleRel.query.filter_by(USER_NO=user_no).first()
        if not user_role:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user_no} ] msg:[ 查询用户角色失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询角色信息
        role = TRole.query.filter_by(ROLE_NO=user_role.ROLE_NO, STATE='ENABLE').first()
        if not role:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user_no} ] roleNo:[ {user_role.ROLE_NO} ] msg:[ 查询角色信息失败 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 判断权限状态是否已禁用
        if role.STATE != 'ENABLE':
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user_no} ] roleNo:[ {role.ROLE_NO} ] roleName:[ {role.ROLE_NAME} ]'
                f'msg:[ 角色状态异常 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        # 查询角色权限关联关系
        role_permission_rel = TRolePermissionRel.query.filter_by(
            ROLE_NO=user_role.ROLE_NO, PERMISSION_NO=permission.PERMISSION_NO
        ).first()
        if not role_permission_rel:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user_no} ] roleNo:[ {user_role.ROLE_NO} ] permissionNo:[ {permission.PERMISSION_NO} ]'
                f'msg:[ 查询角色权限关联关系失败，用户无当前请求的权限 ]'
            )
            return __auth_fail_response(ErrorCode.E401002)

        return func(*args, **kwargs)

    return wrapper


def __auth_fail_response(error: ErrorCode):
    user_no = Global.user_no
    log.info(
        f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
        f'header:[ {dict(request.headers)} ] userNo:[ {user_no} ]'
    )
    res = ResponseDTO(error=error)
    http_res = http_response(res)
    log.info(
        f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
        f'header:[ {dict(http_res.headers)}] response:[ {res} ]'
    )
    return http_res
