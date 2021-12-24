#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : require.py
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
from datetime import datetime
from functools import wraps

from flask import g
from flask import request
from sqlalchemy import and_
from sqlalchemy import or_

from app.common import globals
from app.common.exceptions import ErrorCode
from app.common.response import ResponseDTO
from app.common.response import http_response
from app.extension import db
from app.usercenter.model import TPermission
from app.usercenter.model import TRole
from app.usercenter.model import TRolePermission
from app.usercenter.model import TUser
from app.usercenter.model import TUserPassword
from app.usercenter.model import TUserRole
from app.utils.log_util import get_logger


log = get_logger(__name__)


def require_login(func):
    """登录校验装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_no = globals.get_userno()
        issued_at = globals.get_issued_at()

        # 用户不存在
        user = TUser.filter_by(USER_NO=user_no).first()
        if not user:
            log.info(f'logId:[ {g.logid} ] 用户不存在')
            return check_failed_response(ErrorCode.E401001)

        # 用户未登录，请先登录
        if not user.LOGGED_IN:
            log.info(f'logId:[ {g.logid} ] 用户未登录，请先登录')
            return check_failed_response(ErrorCode.E401001)

        # 用户状态异常
        if user.STATE != 'ENABLE':
            log.info(f'logId:[ {g.logid} ] user.state:[ {user.STATE} ] 用户状态异常')
            return check_failed_response(ErrorCode.E401001)

        # 用户最后成功登录时间和 token 签发时间不一致，即 token 已失效
        user_password = TUserPassword.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()
        if datetime.fromtimestamp(issued_at) != user_password.LAST_SUCCESS_TIME:
            log.info(
                f'logId:[ {g.logid} ] '
                f'签发时间:[ {datetime.fromtimestamp(issued_at)} ] '
                f'最后成功登录时间:[ {user_password.LAST_SUCCESS_TIME} ] '
                f'Token 已失效'
            )
            return check_failed_response(ErrorCode.E401001)

        globals.put('operator', user.USER_NAME)
        return func(*args, **kwargs)

    return wrapper


def require_permission(func):
    """权限校验装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取登录用户
        user_no = globals.get_userno()
        if not user_no:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'获取 flask.g.user_no失败'
            )
            return check_failed_response(ErrorCode.E401002)

        # 查询用户角色关联
        user_role_list = TUserRole.filter_by(USER_NO=user_no).all()
        if not user_role_list:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'userNo:[ {user_no} ] 查询用户角色失败'
            )
            return check_failed_response(ErrorCode.E401002)

        # 查询用户角色权限信息
        roles = [user_role.ROLE_NO for user_role in user_role_list]
        conds = [
            TRole.DELETED == 0,
            TRole.STATE == 'ENABLE',
            TRole.ROLE_NO.in_(roles),
            TPermission.DELETED == 0,
            TPermission.STATE == 'ENABLE',
            TPermission.METHOD == request.method,
            TPermission.ENDPOINT == request.path,
            TRolePermission.DELETED == 0,
            TRolePermission.ROLE_NO == TRole.ROLE_NO,
            TRolePermission.PERMISSION_NO == TPermission.PERMISSION_NO
        ]
        role_permission_list = db.session.query(
            TPermission.PERMISSION_NO,
        ).filter(or_(  # 超级管理员无需校验权限
            and_(*conds),
            and_(TRole.ROLE_NO.in_(roles), TRole.ROLE_CODE == 'SuperAdmin')
        )).first()

        # 判断权限是否存在且状态正常
        if not role_permission_list:
            log.info(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'角色无此权限，或状态异常'
            )
            return check_failed_response(ErrorCode.E401002)

        return func(*args, **kwargs)

    return wrapper


def check_failed_response(error: ErrorCode):
    user_no = globals.get_userno()
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
