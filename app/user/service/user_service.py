#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime
from datetime import timedelta

from app.common.decorators.service import http_service
from app.common.decorators.transaction import db_transaction
from app.common.exceptions import ServiceError
from app.common.flask_helper import Global
from app.common.id_generator import new_id
from app.common.request import RequestDTO
from app.common.validator import assert_blank
from app.common.validator import assert_not_blank
from app.user.model import TRole
from app.user.model import TUser
from app.user.model import TUserAccessToken
from app.user.model import TUserLoginInfo
from app.user.model import TUserLoginLog
from app.user.model import TUserPassword
from app.user.model import TUserPasswordKey
from app.user.model import TUserRoleRel
from app.utils.auth import JWTAuth
from app.utils.log_util import get_logger
from app.utils.rsa_util import decrypt_by_rsa_private_key
from app.utils.security import check_password
from app.utils.security import encrypt_password


log = get_logger(__name__)


@http_service
def login(req: RequestDTO):
    # 查询用户登录信息
    user_login_info = TUserLoginInfo.query_by(LOGIN_NAME=req.loginName).first()
    assert_not_blank(user_login_info, '账号或密码不正确')

    # 查询用户信息
    user = TUser.query_by(USER_NO=user_login_info.USER_NO).first()
    assert_not_blank(user, '账号或密码不正确')

    # 校验用户状态
    if user.STATE != 'ENABLE':
        raise ServiceError('用户状态异常')

    # 查询用户密码
    user_password = TUserPassword.query_by(USER_NO=user.USER_NO, PASSWORD_TYPE='LOGIN').first()
    assert_not_blank(user_password, '账号或密码不正确')

    # 密码RSA解密
    user_password_key = TUserPasswordKey.query_by(LOGIN_NAME=req.loginName).first()
    rsa_private_key = user_password_key.PASSWORD_KEY
    ras_decrypted_password = decrypt_by_rsa_private_key(req['password'], rsa_private_key)

    # 密码校验失败
    if not check_password(req.loginName, user_password.PASSWORD, ras_decrypted_password):
        user_password.LAST_ERROR_TIME = datetime.utcnow()
        if user_password.ERROR_TIMES < 3:
            user_password.ERROR_TIMES += 1
        user_password.save()
        raise ServiceError('账号或密码不正确')

    # 密码校验通过后生成access token
    user_token = TUserAccessToken.query_by(USER_NO=user.USER_NO).first()
    login_time = datetime.utcnow()
    access_token = JWTAuth.encode_auth_token(user.USER_NO, login_time.timestamp())
    expire_in = login_time + timedelta(days=0, seconds=JWTAuth.EXPIRE_TIME)

    # 更新用户access token
    if user_token:
        user_token.update(
            ACCESS_TOKEN=access_token,
            STATE='VALID',
            EXPIRE_IN=expire_in,
        )
    else:
        TUserAccessToken.create(
            USER_NO=user.USER_NO,
            ACCESS_TOKEN=access_token,
            EXPIRE_IN=expire_in,
            STATE='VALID'
        )

    # 更新用户登录时间息
    user_password.update(
        LAST_SUCCESS_TIME=login_time,
        ERROR_TIMES=0
    )

    # 记录用户登录日志
    TUserLoginLog.create(
        USER_NO=user_login_info.USER_NO,
        LOGIN_NAME=user_login_info.LOGIN_NAME,
        LOGIN_TYPE=user_login_info.LOGIN_TYPE,
        IP=''
    )

    # 设置全局操作员
    Global.set('operator', user.USER_NAME)
    return {'accessToken': access_token}


@http_service
def logout():
    user_token = TUserAccessToken.query_by(USER_NO=Global.user_no).first()
    user_token.STATE = 'INVALID'
    user_token.save()
    return None


@http_service
@db_transaction
def register(req: RequestDTO):
    # 查询用户登录信息
    user_login_info = TUserLoginInfo.query_by(LOGIN_NAME=req.loginName).first()
    assert_blank(user_login_info, '登录账号已存在')

    user = TUser.query_by(USER_NAME=req.userName, MOBILE_NO=req.mobileNo, EMAIL=req.email).first()
    assert_blank(user, '用户已存在')

    # 创建用户信息
    user_no = new_id()
    TUser.create(
        commit=False,
        USER_NO=user_no,
        USER_NAME=req.userName,
        MOBILE_NO=req.mobileNo,
        EMAIL=req.email,
        STATE='ENABLE'
    )

    # 创建用户登录信息
    TUserLoginInfo.create(
        commit=False,
        USER_NO=user_no,
        LOGIN_NAME=req.loginName,
        LOGIN_TYPE='ACCOUNT'
    )

    # 创建用户登录密码
    TUserPassword.create(
        commit=False,
        USER_NO=user_no,
        PASSWORD=encrypt_password(req.loginName, req.password),
        PASSWORD_TYPE='LOGIN',
        CREATE_TYPE='CUSTOMER'
    )

    return None


@http_service
def reset_login_password(req: RequestDTO):
    user = TUser.query_by(USER_NO=req.userNo).first()
    assert_not_blank(user, '用户不存在')

    user_password = TUserPassword.query_by(USER_NO=req.userNo, PASSWORD_TYPE='LOGIN').first()
    assert_not_blank(user_password, '用户登录密码不存在')

    user_password.update(PASSWORD=encrypt_password(req.loginName, req.password))
    return None


@http_service
def query_user_list(req: RequestDTO):
    # 查询条件
    conditions = [TUser.DEL_STATE == 0]

    if req.userNo:
        conditions.append(TUser.USER_NO.like(f'%{req.userNo}%'))
    if req.userName:
        conditions.append(TUser.USER_NAME.like(f'%{req.userName}%'))
    if req.mobileNo:
        conditions.append(TUser.MOBILE_NO.like(f'%{req.mobileNo}%'))
    if req.email:
        conditions.append(TUser.EMAIL.like(f'%{req.email}%'))
    if req.state:
        conditions.append(TUser.STATE.like(f'%{req.state}%'))

    pagination = TUser.query.filter(
        *conditions).order_by(TUser.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        user_roles = TUserRoleRel.query_by(USER_NO=item.USER_NO).all()
        roles = []
        for user_role in user_roles:
            role = TRole.query_by(ROLE_NO=user_role.ROLE_NO).first()
            if not role:
                continue
            roles.append(role.ROLE_NAME)
        data_set.append({
            'userNo': item.USER_NO,
            'userName': item.USER_NAME,
            'mobileNo': item.MOBILE_NO,
            'email': item.EMAIL,
            'avatar': item.AVATAR,
            'state': item.STATE,
            'roles': roles
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_user_all():
    users = TUser.query_by().order_by(TUser.CREATED_TIME.desc()).all()
    result = []
    for user in users:
        result.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME
        })
    return result


@http_service
def query_user_info():
    user_no = Global.user_no
    user = TUser.query_by(USER_NO=user_no).first()
    user_roles = TUserRoleRel.query_by(USER_NO=user_no).all()
    roles = []
    for user_role in user_roles:
        role = TRole.query_by(ROLE_NO=user_role.ROLE_NO).first()
        if not role:
            continue
        roles.append(role.ROLE_NAME)
    return {
        'userNo': user_no,
        'userName': user.USER_NAME,
        'mobileNo': user.MOBILE_NO,
        'email': user.EMAIL,
        'avatar': user.AVATAR,
        'roles': roles
    }


@http_service
def modify_user(req: RequestDTO):
    user = TUser.query_by(USER_NO=req.userNo).first()
    assert_not_blank(user, '用户不存在')

    if req.userName is not None:
        user.USER_NAME = req.userName
    if req.mobileNo is not None:
        user.MOBILE_NO = req.mobileNo
    if req.email is not None:
        user.EMAIL = req.email

    user.save()
    return None


@http_service
def modify_user_state(req: RequestDTO):
    user = TUser.query_by(USER_NO=req.userNo).first()
    assert_not_blank(user, '用户不存在')

    user.update(STATE=req.state)
    return None


@http_service
@db_transaction
def delete_user(req: RequestDTO):
    user_no = req.userNo
    user = TUser.query_by(USER_NO=user_no).first()
    assert_not_blank(user, '用户不存在')

    # 删除用户
    user.update(commit=False, DEL_STATE=1)
    # 删除用户角色关联关系
    user_roles = TUserRoleRel.query_by(USER_NO=user_no).all()
    for user_role in user_roles:
        user_role.update(commit=False, DEL_STATE=1)
    # 删除用户登录信息
    user_login_infos = TUserLoginInfo.query_by(USER_NO=user_no).all()
    for user_login_info in user_login_infos:
        user_login_info.update(commit=False, DEL_STATE=1)
    # 删除用户登录历史记录
    user_login_logs = TUserLoginLog.query_by(USER_NO=user_no).all()
    for user_login_log in user_login_logs:
        user_login_log.update(commit=False, DEL_STATE=1)
    # 删除用户密码
    user_passwords = TUserPassword.query_by(USER_NO=user_no).all()
    for user_password in user_passwords:
        user_password.update(commit=False, DEL_STATE=1)
    # 删除用户密码秘钥
    for user_login_info in user_login_infos:
        user_password_key = TUserPasswordKey.query_by(LOGIN_NAME=user_login_info.LOGIN_NAME).first()
        if user_password_key:
            user_password_key.update(commit=False, DEL_STATE=1)
    # 删除用户令牌
    user_access_token = TUserAccessToken.query_by(USER_NO=user_no).first()
    if user_access_token:
        user_access_token.update(commit=False, DEL_STATE=1)

    return None
