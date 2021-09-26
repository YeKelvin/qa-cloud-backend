#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from app.common import global_variables as gvars
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUserRel
from app.user.dao import role_dao as RoleDao
from app.user.dao import user_dao as UserDao
from app.user.dao import user_login_info_dao as UserLoginInfoDao
from app.user.dao import user_login_log_dao as UserLoginLogDao
from app.user.dao import user_password_dao as UserPasswordDao
from app.user.dao import user_password_key_dao as UserPasswordKeyDao
from app.user.dao import user_role_rel_dao as UserRoleRelDao
from app.user.enum import UserState
from app.user.model import TUser
from app.user.model import TUserLoginInfo
from app.user.model import TUserLoginLog
from app.user.model import TUserPassword
from app.utils.auth import JWTAuth
from app.utils.log_util import get_logger
from app.utils.rsa_util import decrypt_by_rsa_private_key
from app.utils.security import check_password
from app.utils.security import encrypt_password
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


log = get_logger(__name__)


@http_service
def login(req):
    # 查询用户登录信息
    login_info = UserLoginInfoDao.select_by_loginname(req.loginName)
    check_is_not_blank(login_info, '账号或密码不正确')

    # 查询用户
    user = UserDao.select_by_userno(login_info.USER_NO)
    check_is_not_blank(user, '账号或密码不正确')

    # 校验用户状态
    if user.STATE != UserState.ENABLE.value:
        raise ServiceError('用户状态异常')

    # 查询用户密码
    user_password = UserPasswordDao.select_loginpwd_by_userno(user.USER_NO)
    check_is_not_blank(user_password, '账号或密码不正确')

    # 密码RSA解密
    user_password_key = UserPasswordKeyDao.select_by_loginname(req.loginName)
    ras_decrypted_password = decrypt_by_rsa_private_key(req.password, user_password_key.PASSWORD_KEY)

    # 校验密码是否正确
    pwd_success = check_password(req.loginName, user_password.PASSWORD, ras_decrypted_password)

    # 密码校验失败
    if not pwd_success:
        user_password.LAST_ERROR_TIME = datetime.utcnow()
        if user_password.ERROR_TIMES < 3:
            user_password.ERROR_TIMES += 1
        raise ServiceError('账号或密码不正确')

    # 密码校验通过后生成token
    issued_at = timestamp_now()
    access_token = JWTAuth.encode_auth_token(user.USER_NO, issued_at)

    # 更新用户登录时间
    # 清空用户登录失败次数
    user_password.update(
        LAST_SUCCESS_TIME=timestamp_to_utc8_datetime(issued_at),
        ERROR_TIMES=0
    )

    # 记录用户登录日志
    # TODO: 记录用户IP
    TUserLoginLog.insert(
        USER_NO=login_info.USER_NO,
        LOGIN_NAME=login_info.LOGIN_NAME,
        LOGIN_TYPE=login_info.LOGIN_TYPE,
        IP=''
    )

    # 更新用户登录状态
    user.update(LOGGED_IN=True)

    # 设置全局操作员
    gvars.put('operator', user.USER_NAME)
    return {'accessToken': access_token}


@http_service
def logout():
    UserDao.logout(gvars.get_userno())


@http_service
@transactional
def register(req):
    # 查询用户登录信息
    login_info = UserLoginInfoDao.select_by_loginname(req.loginName)
    check_is_blank(login_info, '登录账号已存在')

    # 查询用户
    user = UserDao.select_first(USER_NAME=req.userName, MOBILE_NO=req.mobileNo, EMAIL=req.email)
    check_is_blank(user, '用户已存在')

    # 创建用户
    user_no = new_id()
    TUser.insert(
        USER_NO=user_no,
        USER_NAME=req.userName,
        MOBILE_NO=req.mobileNo,
        EMAIL=req.email,
        STATE='ENABLE'
    )

    # 创建用户登录信息
    TUserLoginInfo.insert(
        USER_NO=user_no,
        LOGIN_NAME=req.loginName,
        LOGIN_TYPE='ACCOUNT'
    )

    # 创建用户登录密码
    TUserPassword.insert(
        USER_NO=user_no,
        PASSWORD=encrypt_password(req.loginName, req.password),
        PASSWORD_TYPE='LOGIN',
        CREATE_TYPE='CUSTOMER'
    )

    # 创建私有空间
    worksapce_no = new_id()
    TWorkspace.insert(
        WORKSPACE_NO=worksapce_no,
        WORKSPACE_NAME=f'{req.userName}的私有空间',
        WORKSPACE_SCOPE='PRIVATE'
    )
    TWorkspaceUserRel.insert(WORKSPACE_NO=worksapce_no, USER_NO=user_no)


@http_service
def reset_login_password(req):
    # 查询用户
    user = UserDao.select_by_userno(req.userNo)
    check_is_not_blank(user, '用户不存在')

    # 查询用户密码
    user_password = UserPasswordDao.select_loginpwd_by_userno(req.userNo)
    check_is_not_blank(user_password, '用户登录密码不存在')

    # 更新用户密码
    user_password.update(PASSWORD=encrypt_password(req.loginName, req.password))


@http_service
def query_user_list(req):
    # 查询条件
    conds = QueryCondition(TUser, TUserLoginInfo)
    conds.like(TUser.USER_NO, req.userNo)
    conds.like(TUser.USER_NAME, req.userName)
    conds.like(TUser.MOBILE_NO, req.mobileNo)
    conds.like(TUser.EMAIL, req.email)
    conds.like(TUser.STATE, req.state)
    conds.equal(TUser.USER_NO, TUserLoginInfo.USER_NO)
    conds.equal(TUserLoginInfo.LOGIN_TYPE, 'ACCOUNT')
    conds.equal(TUserLoginInfo.LOGIN_NAME, req.loginName)

    # 查询用户列表
    pagination = db.session.query(
        TUser.USER_NO,
        TUser.USER_NAME,
        TUser.MOBILE_NO,
        TUser.EMAIL,
        TUser.STATE,
        TUser.AVATAR,
        TUserLoginInfo.LOGIN_NAME
    ).filter(*conds).order_by(TUser.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for user in pagination.items:
        # 查询用户绑定的角色列表
        user_role_list = UserRoleRelDao.select_all_by_userno(user.USER_NO)
        roles = []
        for user_role in user_role_list:
            # 查询角色
            role = RoleDao.select_by_roleno(user_role.ROLE_NO)
            if not role:
                continue
            roles.append(role.ROLE_NAME)

        data.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'loginName': user.LOGIN_NAME,
            'mobileNo': user.MOBILE_NO,
            'email': user.EMAIL,
            'avatar': user.AVATAR,
            'state': user.STATE,
            'roles': roles
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_user_all():
    # 查询所有用户
    users = UserDao.select_all()

    result = []
    for user in users:
        result.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'state': user.STATE
        })
    return result


@http_service
def query_user_info():
    user_no = gvars.get_userno()

    # 查询用户
    user = UserDao.select_by_userno(user_no)
    # 查询用户绑定的角色列表
    user_role_list = UserRoleRelDao.select_all_by_userno(user_no)

    roles = []
    for user_role in user_role_list:
        # 查询角色
        role = RoleDao.select_by_roleno(user_role.ROLE_NO)
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
def modify_user(req):
    # 查询用户
    user = UserDao.select_by_userno(req.userNo)
    check_is_not_blank(user, '用户不存在')

    # 更新用户信息
    user.update(
        USER_NAME=req.userName,
        MOBILE_NO=req.mobileNo,
        EMAIL=req.email
    )
    # TODO: workspaceName也要同步修改


@http_service
def modify_user_state(req):
    # 查询用户
    user = UserDao.select_by_userno(req.userNo)
    check_is_not_blank(user, '用户不存在')

    # 更新用户状态
    user.update(STATE=req.state)


@http_service
@transactional
def remove_user(req):
    # 查询用户
    user = UserDao.select_by_userno(req.userNo)
    check_is_not_blank(user, '用户不存在')

    # 解绑用户和角色
    UserRoleRelDao.delete_all_by_userno(req.userNo)

    # 删除用户密码
    UserPasswordDao.delete_all_by_user_no(req.userNo)

    # 删除用户密码秘钥 TODO: 优化删除逻辑
    for login_info in UserLoginInfoDao.select_all_by_userno(req.userNo):
        UserPasswordKeyDao.delete_by_loginname(login_info.LOGIN_NAME)

    # 删除用户登录历史记录
    UserLoginLogDao.delete_all_by_userno(req.userNo)

    # 删除用户登录信息
    UserLoginInfoDao.delete_all_by_userno(req.userNo)

    # 删除用户
    user.delete()
    # TODO: 私有空间也要删除
