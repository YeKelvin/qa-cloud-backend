#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from flask import request

from app.extension import db
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUser
from app.tools import globals
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.usercenter.dao import group_dao as GroupDao
from app.usercenter.dao import role_dao as RoleDao
from app.usercenter.dao import user_dao as UserDao
from app.usercenter.dao import user_group_dao as UserGroupDao
from app.usercenter.dao import user_login_info_dao as UserLoginInfoDao
from app.usercenter.dao import user_login_log_dao as UserLoginLogDao
from app.usercenter.dao import user_password_dao as UserPasswordDao
from app.usercenter.dao import user_password_key_dao as UserPasswordKeyDao
from app.usercenter.dao import user_role_dao as UserRoleDao
from app.usercenter.enum import UserState
from app.usercenter.model import TGroup
from app.usercenter.model import TGroupRole
from app.usercenter.model import TRole
from app.usercenter.model import TUser
from app.usercenter.model import TUserGroup
from app.usercenter.model import TUserLoginInfo
from app.usercenter.model import TUserLoginLog
from app.usercenter.model import TUserPassword
from app.usercenter.model import TUserRole
from app.utils.auth import JWTAuth
from app.utils.rsa_util import decrypt_by_rsa_private_key
from app.utils.security import check_password
from app.utils.security import encrypt_password
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


from datetime import timezone
log = get_logger(__name__)


@http_service
@transactional
def login(req):
    # 查询用户登录信息
    login_info = UserLoginInfoDao.select_by_loginname(req.loginName)
    check_exists(login_info, error_msg='账号或密码不正确')

    # 查询用户
    user = UserDao.select_by_no(login_info.USER_NO)
    check_exists(user, error_msg='账号或密码不正确')

    # 校验用户状态
    if user.STATE != UserState.ENABLE.value:
        raise ServiceError('用户状态异常')

    # 查询用户密码
    user_password = UserPasswordDao.select_loginpwd_by_user(user.USER_NO)
    check_exists(user_password, error_msg='账号或密码不正确')

    # 密码RSA解密
    user_password_key = UserPasswordKeyDao.select_by_loginname(req.loginName)
    ras_decrypted_password = decrypt_by_rsa_private_key(req.password, user_password_key.PASSWORD_KEY)

    # 校验密码是否正确
    pwd_success = check_password(req.loginName, user_password.PASSWORD, ras_decrypted_password)

    # 密码校验失败
    if not pwd_success:
        user_password.LAST_ERROR_TIME = datetime.now(timezone.utc)
        if user_password.ERROR_TIMES < 3:
            user_password.ERROR_TIMES += 1
        raise ServiceError('账号或密码不正确')

    # 密码校验通过后生成token
    issued_at = timestamp_now()
    token = JWTAuth.encode_token(user.USER_NO, issued_at)

    # 更新用户登录时间
    # 清空用户登录失败次数
    user_password.update(
        LAST_SUCCESS_TIME=timestamp_to_utc8_datetime(issued_at),
        ERROR_TIMES=0
    )

    # 记录用户登录日志
    TUserLoginLog.insert(
        USER_NO=login_info.USER_NO,
        LOGIN_NAME=login_info.LOGIN_NAME,
        LOGIN_TYPE=login_info.LOGIN_TYPE,
        IP=remote_addr()
    )

    # 更新用户登录状态
    user.update(LOGGED_IN=True)

    return {'accessToken': token}


def remote_addr():
    if x_forwarded_for := request.headers.get('X-Forwarded-For'):
        ip_list = x_forwarded_for.split(',')
        return ip_list[0]
    else:
        return request.remote_addr


@http_service
@transactional
def logout():
    # 查询用户
    user = UserDao.select_by_no(globals.get_userno())
    check_exists(user, error_msg='用户不存在')
    # 登出
    user.update(LOGGED_IN=False)


@http_service
@transactional
def register(req):
    # 查询用户登录信息
    login_info = UserLoginInfoDao.select_by_loginname(req.loginName)
    check_not_exists(login_info, error_msg='登录账号已存在')

    # 查询用户
    user = UserDao.select_first(USER_NAME=req.userName, MOBILE_NO=req.mobileNo, EMAIL=req.email)
    check_not_exists(user, error_msg='用户已存在')

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

    # 创建个人空间
    worksapce_no = new_id()
    TWorkspace.insert(
        WORKSPACE_NO=worksapce_no,
        WORKSPACE_NAME=f'{req.userName}的个人空间',
        WORKSPACE_SCOPE='PRIVATE'
    )
    TWorkspaceUser.insert(WORKSPACE_NO=worksapce_no, USER_NO=user_no)

    # 绑定用户角色
    if req.roleNos:
        for role_no in req.roleNos:
            TUserRole.insert(USER_NO=user_no, ROLE_NO=role_no)

    # 绑定用户分组
    if req.groupNos:
        for group_no in req.groupNos:
            TUserGroup.insert(USER_NO=user_no, GROUP_NO=group_no)


@http_service
@transactional
def reset_login_password(req):
    # 查询用户
    user = UserDao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 查询登录信息
    user_login_info = UserLoginInfoDao.select_by_user(req.userNo)
    check_exists(user_login_info, error_msg='用户登录信息不存在')

    # 查询用户密码
    user_password = UserPasswordDao.select_loginpwd_by_user(req.userNo)
    check_exists(user_password, error_msg='用户登录密码不存在')

    # 更新用户密码
    user_password.update(PASSWORD=encrypt_password(user_login_info.LOGIN_NAME, '123456'))


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
    ).filter(*conds).order_by(TUser.CREATED_TIME.desc()).paginate(page=req.page, per_page=req.pageSize)

    data = []
    for user in pagination.items:
        # 跳过 administrator 用户
        if user.LOGIN_NAME == 'admin':
            continue
        # 查询用户绑定的角色列表
        roles = []
        user_role_list = UserRoleDao.select_all_by_userno(user.USER_NO)
        for user_role in user_role_list:
            # 查询角色
            role = RoleDao.select_by_no(user_role.ROLE_NO)
            if not role:
                continue
            roles.append({
                'roleNo': role.ROLE_NO,
                'roleName': role.ROLE_NAME
            })
        # 查询用户分组列表
        groups = []
        user_group_list = UserGroupDao.select_all_by_user(user.USER_NO)
        for user_group in user_group_list:
            # 查询分组
            group = GroupDao.select_by_no(user_group.GROUP_NO)
            if not group:
                continue
            groups.append({
                'groupNo': group.GROUP_NO,
                'groupName': group.GROUP_NAME
            })

        data.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'loginName': user.LOGIN_NAME,
            'mobileNo': user.MOBILE_NO,
            'email': user.EMAIL,
            'avatar': user.AVATAR,
            'state': user.STATE,
            'roles': roles,
            'groups': groups
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_user_all():
    # 查询条件
    conds = QueryCondition(TUser, TUserLoginInfo)
    conds.equal(TUser.USER_NO, TUserLoginInfo.USER_NO)

    # 查询用户列表
    users = db.session.query(
        TUser.USER_NO,
        TUser.USER_NAME,
        TUser.STATE,
        TUserLoginInfo.LOGIN_NAME
    ).filter(*conds).order_by(TUser.CREATED_TIME.desc()).all()

    result = []
    for user in users:
        # 跳过 administrator 用户
        if user.LOGIN_NAME == 'admin':
            continue
        result.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'state': user.STATE
        })
    return result


def get_user_roles(user_no):
    user_roles = db.session.query(
        TRole.ROLE_CODE
    ).filter(
        TRole.DELETED == 0,
        TUserRole.DELETED == 0,
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO == TRole.ROLE_NO
    )
    group_roles = db.session.query(
        TRole.ROLE_CODE
    ).filter(
        TGroup.DELETED == 0,
        TRole.DELETED == 0,
        TUserGroup.DELETED == 0,
        TUserGroup.USER_NO == user_no,
        TUserGroup.GROUP_NO == TGroup.GROUP_NO,
        TGroupRole.DELETED == 0,
        TGroupRole.ROLE_NO == TRole.ROLE_NO,
        TGroupRole.GROUP_NO == TUserGroup.GROUP_NO
    )
    return user_roles.union(group_roles).all()


@http_service
def query_user_info():
    # 获取用户编号
    user_no = globals.get_userno()
    # 查询用户
    user = UserDao.select_by_no(user_no)
    # 查询用户角色
    roles = [role.ROLE_CODE for role in get_user_roles(user_no)]

    return {
        'userNo': user_no,
        'userName': user.USER_NAME,
        'mobileNo': user.MOBILE_NO,
        'email': user.EMAIL,
        'avatar': user.AVATAR,
        'roles': roles
    }


@http_service
@transactional
def modify_user(req):
    # 查询用户
    user = UserDao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 更新用户信息
    user.update(
        USER_NAME=req.userName,
        MOBILE_NO=req.mobileNo,
        EMAIL=req.email
    )

    # 同步修改私人空间名称
    workspace = get_private_workspace_by_user(req.userNo)
    workspace.update(WORKSPACE_NAME=f'{req.userName}的个人空间')

    # 绑定用户角色
    if req.roleNos is not None:
        for role_no in req.roleNos:
            # 查询用户角色
            user_role = UserRoleDao.select_by_user_and_role(req.userNo, role_no)
            if not user_role:
                TUserRole.insert(USER_NO=req.userNo, ROLE_NO=role_no)

        # 删除不在请求中的角色
        UserRoleDao.delete_all_by_user_and_notin_role(req.userNo, req.roleNos)

    # 绑定用户分组
    if req.groupNos is not None:
        for group_no in req.groupNos:
            # 查询用户分组
            group_user = UserGroupDao.select_by_user_and_group(req.userNo, group_no)
            if not group_user:
                TUserGroup.insert(USER_NO=req.userNo, GROUP_NO=group_no)

        # 解绑不在请求中的分组
        UserGroupDao.delete_all_by_user_and_notin_group(req.userNo, req.groupNos)


def get_private_workspace_by_user(user_no):
    # 查询条件
    conds = QueryCondition(TWorkspace, TWorkspaceUser)
    conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    conds.equal(TWorkspace.WORKSPACE_SCOPE, 'PRIVATE')
    conds.equal(TWorkspaceUser.USER_NO, user_no)

    # 查询私人空间
    return db.session.query(TWorkspace).filter(*conds).first()


@http_service
@transactional
def modify_user_state(req):
    # 查询用户
    user = UserDao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 更新用户状态
    user.update(STATE=req.state)


@http_service
@transactional
def remove_user(req):
    # 查询用户
    user = UserDao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 删除用户角色
    UserRoleDao.delete_all_by_user(req.userNo)

    # 删除用户分组
    UserGroupDao.delete_all_by_user(req.userNo)

    # 删除用户密码
    UserPasswordDao.delete_all_by_user(req.userNo)

    # 删除用户密码秘钥
    login_info_list = UserLoginInfoDao.select_all_by_user(req.userNo)
    for login_info in login_info_list:
        UserPasswordKeyDao.delete_by_loginname(login_info.LOGIN_NAME)

    # 删除用户登录历史记录
    UserLoginLogDao.delete_all_by_user(req.userNo)

    # 删除用户登录账号
    UserLoginInfoDao.delete_all_by_user(req.userNo)

    # 删除私人空间
    workspace = get_private_workspace_by_user(req.userNo)
    workspace.delete()

    # 删除空间成员
    TWorkspaceUser.deletes(TWorkspaceUser.USER_NO == req.userNo)

    # 删除用户
    user.delete()
