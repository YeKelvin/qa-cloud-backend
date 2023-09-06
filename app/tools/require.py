#!/usr/bin/ python3
# @File    : require.py
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
from datetime import datetime
from functools import wraps

import jwt

from flask import g
from flask import request
from loguru import logger

from app.extension import db
from app.modules.opencenter.model import TThirdPartyApplication
from app.modules.usercenter.model import TGroup
from app.modules.usercenter.model import TGroupRole
from app.modules.usercenter.model import TPermission
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TRolePermission
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserGroup
from app.modules.usercenter.model import TUserPassword
from app.modules.usercenter.model import TUserRole
from app.tools import localvars
from app.tools.auth import JWTAuth
from app.tools.exceptions import ErrorCode
from app.tools.response import ResponseDTO
from app.tools.response import http_response


def require_login(func):
    """登录校验装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_no = None
        issued_at = None
        # 校验access-token
        if 'access-token' not in request.headers:
            # 缺失请求头
            return failed_response(ErrorCode.E401001, msg='请求头缺失access-token')
        # 获取access-token
        access_toekn = request.headers.get('access-token')
        try:
            # 解析token，获取payload
            payload = JWTAuth.decode_token(access_toekn)
            user_no = payload['data']['id']
            issued_at = payload['iat']
            # 存储用户编号
            localvars.set('user_no', user_no)
        except jwt.ExpiredSignatureError:
            return failed_response(ErrorCode.E401001, msg='token已失效')
        except jwt.InvalidTokenError:
            return failed_response(ErrorCode.E401001, msg='无效的token')
        except Exception:
            logger.bind(traceid=g.trace_id).exception()
            return failed_response(ErrorCode.E500000)

        # 用户不存在
        user = TUser.filter_by(USER_NO=user_no).first()
        if not user:
            logger.bind(traceid=g.trace_id).info('用户不存在')
            return failed_response(ErrorCode.E401001)

        # 用户未登录，请先登录
        if not user.LOGGED_IN:
            logger.bind(traceid=g.trace_id).info('用户未登录')
            return failed_response(ErrorCode.E401001)

        # 用户状态异常
        if user.STATE != 'ENABLE':
            logger.bind(traceid=g.trace_id).info('用户状态异常')
            return failed_response(ErrorCode.E401001)

        # 用户最后成功登录时间和 token 签发时间不一致，即 token 已失效
        user_password = TUserPassword.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()
        # 非平台用户不校验最后成功登录时间和签发时间
        if user_password and datetime.fromtimestamp(issued_at) != user_password.LAST_SUCCESS_TIME:
            logger.bind(traceid=g.trace_id).info('token已失效')
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
                logger.bind(traceid=g.trace_id).info(
                    f'method:[ {request.method} ] path:[ {request.path} ] 获取用户编号失败'
                )
                return failed_response(ErrorCode.E401002)

            # 查询用户权限，判断权限是否存在且状态正常
            if exists_user_permission(user_no, code):
                localvars.set('permission_code', code)  # 存储权限唯一代码
                return func(*args, **kwargs)

            # 超级管理员无需校验权限
            if is_super_admin(user_no):
                return func(*args, **kwargs)

            # 其余情况校验不通过
            logger.bind(traceid=g.trace_id).info(
                f'method:[ {request.method} ] path:[ {request.path} ] 角色无此权限，或状态异常'
            )
            return failed_response(ErrorCode.E401002)

        return wrapper

    return middleware


def require_thirdparty_access(func):
    """OpenAPI校验装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 从请求头中获取app信息
        appno = request.headers['app-no']
        appsecret = request.headers['app-secret']
        # 校验密钥
        tpa = (
            TThirdPartyApplication
            .filter_by(APP_NO=appno, APP_SECRET=appsecret)
            .first()
        )
        # 应用不存在
        if not tpa:
            logger.bind(traceid=g.trace_id).info('第三方应用不存在')
            return failed_response(ErrorCode.E401003)
        # 应用状态异常
        if tpa.STATE != 'ENABLE':
            logger.bind(traceid=g.trace_id).info('第三方应用状态异常')
            return failed_response(ErrorCode.E401003)
        # 存储appno
        localvars.set('thirdparty_app_no', appno)
        return func(*args, **kwargs)

    return wrapper


def failed_response(error: ErrorCode, msg=None):
    logger.bind(traceid=g.trace_id).info(
        f'uri:[ {request.method} {request.path} ] '
        f'header:[ {dict(request.headers)} ] request:[ {request.values} ]'
    )
    res = ResponseDTO(error=error, errorMsg=msg)
    http_res = http_response(res)
    logger.bind(traceid=g.trace_id).info(
        f'uri:[ {request.method} {request.path} ] '
        f'header:[ {dict(http_res.headers)}] response:[ {res} ]'
    )
    return http_res


def get_user_roles(user_no):
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
        TRolePermission.ROLE_NO.in_(get_user_roles(user_no)),
        TRolePermission.PERMISSION_NO == TPermission.PERMISSION_NO
    ]
    return db.session.query(TPermission.PERMISSION_NO).filter(*conds).first()


def is_super_admin(user_no):
    superadmin = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TRole.ROLE_CODE == 'ADMIN',
        TUserRole.DELETED == 0,
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO == TRole.ROLE_NO
    ).first()
    return bool(superadmin)
