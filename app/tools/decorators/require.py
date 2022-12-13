#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : require.py
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
from datetime import datetime
from functools import wraps

from flask import g
from flask import request

from app.extension import db
from app.tools import localvars
from app.tools.exceptions import ErrorCode
from app.tools.logger import get_logger
from app.tools.response import ResponseDTO
from app.tools.response import http_response
from app.usercenter.model import TGroup
from app.usercenter.model import TGroupRole
from app.usercenter.model import TPermission
from app.usercenter.model import TRole
from app.usercenter.model import TRolePermission
from app.usercenter.model import TUser
from app.usercenter.model import TUserGroup
from app.usercenter.model import TUserPassword
from app.usercenter.model import TUserRole


log = get_logger(__name__)


def require_login(func):
    """登录校验装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_no = localvars.get_user_no()
        issued_at = localvars.get_issued_at()

        # 用户不存在
        user = TUser.filter_by(USER_NO=user_no).first()
        if not user:
            log.info('用户不存在')
            return failed_response(ErrorCode.E401001)

        # 用户未登录，请先登录
        if not user.LOGGED_IN:
            log.info('用户未登录，请先登录')
            return failed_response(ErrorCode.E401001)

        # 用户状态异常
        if user.STATE != 'ENABLE':
            log.info(f'userState:[ {user.STATE} ] 用户状态异常')
            return failed_response(ErrorCode.E401001)

        # 用户最后成功登录时间和 token 签发时间不一致，即 token 已失效
        user_password = TUserPassword.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()
        if datetime.fromtimestamp(issued_at) != user_password.LAST_SUCCESS_TIME:
            log.info(
                f'签发时间:[ {datetime.fromtimestamp(issued_at)} ] '
                f'最后成功登录时间:[ {user_password.LAST_SUCCESS_TIME} ] '
                f'登录失败，Token 已失效'
            )
            return failed_response(ErrorCode.E401001)

        localvars.set('operator', user.USER_NAME)
        return func(*args, **kwargs)

    return wrapper


def require_permission(code):
    """权限校验装饰器"""

    def middleware(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取登录用户
            user_no = localvars.get_user_no()
            if not user_no:
                log.info(f'method:[ {request.method} ] path:[ {request.path} ] 获取用户编号失败')
                return failed_response(ErrorCode.E401002)

            # 查询用户权限，判断权限是否存在且状态正常
            if exists_user_permission(user_no, code):
                localvars.set('permission_code', code)  # 存储权限唯一代码
                return func(*args, **kwargs)

            # 超级管理员无需校验权限
            if is_super_admin(user_no):
                return func(*args, **kwargs)

            # 其余情况校验不通过
            log.info(f'method:[ {request.method} ] path:[ {request.path} ] 角色无此权限，或状态异常')
            return failed_response(ErrorCode.E401002)

        return wrapper

    return middleware


def failed_response(error: ErrorCode):
    log.info(
        f'method:[ {request.method} ] path:[ {request.path} ] '
        f'header:[ {dict(request.headers)} ] request:[ {request.values} ]'
    )
    res = ResponseDTO(error=error)
    http_res = http_response(res)
    log.info(
        f'method:[ {request.method} ] path:[ {request.path} ] '
        f'header:[ {dict(http_res.headers)}] response:[ {res} ]'
    )
    return http_res


def get_user_role_numbers(user_no):
    user_role_stmt = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TUserRole.DELETED == 0,
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO == TRole.ROLE_NO,
    )
    group_role_stmt = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TGroup.DELETED == 0,
        TGroup.STATE == 'ENABLE',
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TUserGroup.DELETED == 0,
        TUserGroup.USER_NO == user_no,
        TUserGroup.GROUP_NO == TGroup.GROUP_NO,
        TGroupRole.DELETED == 0,
        TGroupRole.ROLE_NO == TRole.ROLE_NO,
        TGroupRole.GROUP_NO == TUserGroup.GROUP_NO,
    )
    return [entity.ROLE_NO for entity in user_role_stmt.union(group_role_stmt).all()]


def exists_user_permission(user_no, code):
    conds = [
        TPermission.DELETED == 0,
        TPermission.STATE == 'ENABLE',
        TPermission.PERMISSION_CODE == code,
        TRolePermission.DELETED == 0,
        TRolePermission.ROLE_NO.in_(get_user_role_numbers(user_no)),
        TRolePermission.PERMISSION_NO == TPermission.PERMISSION_NO
    ]
    return db.session.query(TPermission.PERMISSION_NO).filter(*conds).first()


def is_super_admin(user_no):
    superadmin = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TRole.ROLE_CODE == 'SUPER_ADMIN',
        TUserRole.DELETED == 0,
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO == TRole.ROLE_NO
    ).first()
    return bool(superadmin)
