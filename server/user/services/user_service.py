#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from server.common.number_generator import generate_user_no
from server.librarys.decorators.service import http_service
from server.librarys.exception import ServiceError
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.user.model import (TUser, TUserRoleRel, TRole, TUserLoginInfo, TUserPassword, TUserAccessToken,
                               TUserLoginLog, TUserPasswordKey)
from server.user.utils.auth import Auth
from server.utils.log_util import get_logger
from server.utils.rsa_util import decrypt_by_rsa_private_key

log = get_logger(__name__)


@http_service
def login(req: RequestDTO):
    # 查询用户登录信息
    user_login_info = TUserLoginInfo.query.filter_by(LOGIN_NAME=req.attr.loginName, DEL_STATE=0).first()
    Verify.not_empty(user_login_info, '账号或密码不正确')

    # 查询用户信息
    user = TUser.query.filter_by(USER_NO=user_login_info.USER_NO, DEL_STATE=0).first()
    Verify.not_empty(user, '账号或密码不正确')

    # 校验用户状态
    if user.STATE != 'ENABLE':
        raise ServiceError('用户状态异常')

    # 查询用户密码
    user_password = TUserPassword.query.filter_by(
        USER_NO=user_login_info.USER_NO, PASSWORD_TYPE='LOGIN', DEL_STATE=0
    ).first()
    Verify.not_empty(user_password, '账号或密码不正确')

    # 密码RSA解密
    user_password_key = TUserPasswordKey.query.filter_by(LOGIN_NAME=user_login_info.USER_NO, DEL_STATE=0).first()
    rsa_private_key = user_password_key.PASSWORD_KEY
    password = decrypt_by_rsa_private_key(req.attr['password'], rsa_private_key)

    # 密码校验失败
    if not user_password.check_password_hash(req.attr.loginName, password):
        user_password.LAST_ERROR_TIME = datetime.utcnow()
        if user_password.ERROR_TIMES < 3:
            user_password.ERROR_TIMES += 1
        user_password.save()
        raise ServiceError('账号或密码不正确')

    # 密码校验通过后生成access token
    user_token = TUserAccessToken.query.filter_by(LOGIN_NAME=req.attr.loginName, DEL_STATE=0).first()
    login_time = datetime.utcnow()
    access_token = Auth.encode_auth_token(user_login_info.USER_NO, login_time.timestamp())
    expire_in = ...

    # 更新用户access token
    if user_token:
        access_token.update(
            ACCESS_TOKEN=access_token,
            STATE='VALID',
            EXPIRE_IN=expire_in,
        )
    else:
        TUserAccessToken.create(
            USER_NO=user_login_info.USER_NO,
            LOGIN_NAME=req.attr.loginName,
            ACCESS_TOKEN=access_token,
            EXPIRE_IN=expire_in,
            STATE='VALID'
        )

    # 更新用户登录时间息
    user_password.update(
        last_login_time=login_time,
        last_success_time=login_time,
        error_times=0
    )

    # 记录用户登录日志
    TUserLoginLog.create(
        USER_NO=user_login_info.USER_NO,
        LOGIN_NAME=user_login_info.LOGIN_NAME,
        LOGIN_TYPE=user_login_info.LOGIN_TYPE,
        IP=''
    )

    # 设置全局操作员
    Global.set('operator', user_login_info.USER_NO)
    return {'accessToken': access_token}


@http_service
def logout():
    user_token = TUserAccessToken.query.filter_by(USER_NO=Global.user_no, DEL_STATE=0).first()
    user_token.STATE = 'INVALID'
    user_token.save()
    return None


@http_service
def register(req: RequestDTO):
    # 查询用户登录信息
    user_login_info = TUserLoginInfo.query.filter_by(LOGIN_NAME=req.attr.loginName, DEL_STATE=0).first()
    Verify.empty(user_login_info, '登录账号已存在')

    user = TUser.query.filter_by(
        USER_NAME=req.attr.userName, MOBILE_NO=req.attr.mobileNo, EMAIL=req.attr.email, DEL_STATE=0
    ).first()
    Verify.empty(user, '用户已存在')

    # 创建用户信息
    user_no = generate_user_no()
    TUser.create(
        USER_NO=user_no,
        USER_NAME=req.attr.userName,
        MOBILE_NO=req.attr.mobileNo,
        EMAIL=req.attr.email,
        STATE='ENABLE'
    )

    # 创建用户登录信息
    TUserLoginInfo.create(
        USER_NO=user_no,
        LOGIN_NAME=req.attr.loginName,
        LOGIN_TYPE='ACCOUNT'
    )

    # 创建用户登录密码
    TUserPassword.create(
        USER_NO=user_no,
        PASSWORD=TUserPassword.generate_password_hash(req.attr.loginName, req.attr.password),
        PASSWORD_TYPE='LOGIN'
    )

    return None


@http_service
def reset_password(req: RequestDTO):
    user = TUser.query.filter_by(USER_NO=req.attr.userNo, DEL_STATE=0).first()
    Verify.not_empty(user, '用户不存在')

    user.password = '123456'
    user.save()
    return None


@http_service
def query_user_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = [TUser.DEL_STATE == 0]
    if req.attr.userNo:
        conditions.append(TUser.USER_NO.like(f'%{req.attr.userNo}%'))
    if req.attr.userName:
        conditions.append(TUser.USER_NAME.like(f'%{req.attr.userName}%'))
    if req.attr.mobileNo:
        conditions.append(TUser.MOBILE_NO.like(f'%{req.attr.mobileNo}%'))
    if req.attr.email:
        conditions.append(TUser.EMAIL.like(f'%{req.attr.email}%'))
    if req.attr.state:
        conditions.append(TUser.STATE.like(f'%{req.attr.state}%'))

    # 列表总数
    total_size = TUser.query.filter(*conditions).count()
    # 列表数据
    users = TUser.query.filter(*conditions).order_by(TUser.CREATED_TIME.desc()).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for user in users:
        user_roles = TUserRoleRel.query.filter_by(USER_NO=user.USER_NO, DEL_STATE=0).all()
        roles = []
        for user_role in user_roles:
            role = TRole.query.filter_by(ROLE_NO=user_role.ROLE_NO, DEL_STATE=0).first()
            roles.append(role.ROLE_NAME)
        data_set.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'mobileNo': user.MOBILE_NO,
            'email': user.EMAIL,
            'avatar': user.AVATAR,
            'state': user.STATE,
            'roles': roles
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_user_all():
    users = TUser.query.order_by(TUser.CREATED_TIME.desc()).all()
    result = []
    for user in users:
        result.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME
        })
    return result


@http_service
def query_user_info():
    user = Global.user_no
    user_roles = TUserRoleRel.query.filter_by(USER_NO=user.USER_NO, DEL_STATE=0).all()
    roles = []
    for user_role in user_roles:
        role = TRole.query.filter_by(ROLE_NO=user_role.ROLE_NO, DEL_STATE=0).first()
        roles.append(role.ROLE_NAME)
    return {
        'userNo': user.USER_NO,
        'userName': user.USER_NAME,
        'mobileNo': user.MOBILE_NO,
        'email': user.EMAIL,
        'avatar': user.AVATAR,
        'roles': roles
    }


@http_service
def modify_user(req: RequestDTO):
    user = TUser.query.filter_by(USER_NO=req.attr.userNo, DEL_STATE=0).first()
    Verify.not_empty(user, '用户不存在')

    if req.attr.userName is not None:
        user.USER_NAME = req.attr.userName
    if req.attr.mobileNo is not None:
        user.MOBILE_NO = req.attr.mobileNo
    if req.attr.email is not None:
        user.EMAIL = req.attr.email

    user.save()
    return None


@http_service
def modify_user_state(req: RequestDTO):
    user = TUser.query.filter_by(USER_NO=req.attr.userNo, DEL_STATE=0).first()
    Verify.not_empty(user, '用户不存在')

    user.update(STATE=req.attr.state)
    return None


@http_service
def delete_user(req: RequestDTO):
    user = TUser.query.filter_by(USER_NO=req.attr.userNo, DEL_STATE=0).first()
    Verify.not_empty(user, '用户不存在')

    # 删除用户角色关联关系
    user_roles = TUserRoleRel.query.filter_by(USER_NO=req.attr.userNo, DEL_STATE=0).all()
    for user_role in user_roles:
        user_role.update(DEL_STATE=1)

    # 删除用户
    user.update(DEL_STATE=1)
    return None
