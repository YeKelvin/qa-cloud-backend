#!/usr/bin/ python3
# @File    : user_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import UTC
from datetime import datetime

from flask import request
from loguru import logger
from sqlalchemy import or_

from app import config as CONFIG
from app.database import db_query
from app.modules.public.model import TWorkspace
from app.modules.public.model import TWorkspaceUser
from app.modules.script.enum import VariableDatasetWeight
from app.modules.script.model import TVariableDataset
from app.modules.usercenter.dao import group_dao
from app.modules.usercenter.dao import group_member_dao
from app.modules.usercenter.dao import role_dao
from app.modules.usercenter.dao import user_dao
from app.modules.usercenter.dao import user_login_info_dao
from app.modules.usercenter.dao import user_password_dao
from app.modules.usercenter.dao import user_role_dao
from app.modules.usercenter.enum import UserState
from app.modules.usercenter.model import TGroup
from app.modules.usercenter.model import TGroupMember
from app.modules.usercenter.model import TGroupRole
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserLoginInfo
from app.modules.usercenter.model import TUserLoginLog
from app.modules.usercenter.model import TUserPassword
from app.modules.usercenter.model import TUserRole
from app.tools import cache
from app.tools import http_client
from app.tools import localvars
from app.tools.auth import JWTAuth
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.security import check_password
from app.tools.security import encrypt_password
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.utils.rsa_util import decrypt_by_rsa_private_key
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


@http_service
def login(req):
    try:
        # 查询用户登录信息
        login_info = user_login_info_dao.select_by_loginname(req.loginName)
        if not login_info:
            logger.info('用户登录信息不存在')
            raise ServiceError('账号或密码不正确')

        # 查询用户
        user = user_dao.select_by_no(login_info.USER_NO)
        if not user:
            logger.info('用户信息不存在')
            raise ServiceError('账号或密码不正确')
        localvars.set('user_no', user.USER_NO)

        # 校验用户状态
        if user.STATE != UserState.ENABLE.value:
            raise ServiceError('用户状态异常')

        # 查询用户密码
        user_password = user_password_dao.select_loginpwd_by_user(user.USER_NO)
        if not user_password:
            logger.info('用户登录密码不存在')
            raise ServiceError('账号或密码不正确')

        # 密码RSA解密
        secret_key = cache.encryption_factors.get(req.index)
        if not secret_key:
            raise ServiceError('加密因子不存在')
        decrypted_password = decrypt_by_rsa_private_key(req.password, secret_key)

        # 校验密码是否正确
        password_success = check_password(req.loginName, user_password.PASSWORD, decrypted_password)

        # 密码校验失败
        if not password_success:
            logger.info('密码错误')
            user_password.LAST_FAILURE_TIME = datetime.now(UTC)
            if user_password.ERROR_TIMES < 3:
                logger.info('密码错误次数+1')
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
            LOGIN_METHOD='PASSWORD',
            LOGIN_IP=remote_addr(),
            LOGIN_TIME=timestamp_to_utc8_datetime(issued_at)
        )

        # 更新用户登录状态
        user.update(LOGGED_IN=True)
    except Exception:
        raise
    finally:
        # 删除密钥索引
        cache.encryption_factors.pop(req.index)

    return {'accessToken': token}


@http_service
def login_by_enterprise(req):
    if not CONFIG.SSO_ENTERPRISE_URL:
        raise ServiceError('暂未启用企业账号登录')

    # 密码RSA解密
    secret_key = cache.encryption_factors.get(req.index)
    if not secret_key:
        raise ServiceError('加密因子不存在')
    decrypted_password = decrypt_by_rsa_private_key(req.password, secret_key)

    # 企业登录认证
    sso_res = http_client.post(
        url=CONFIG.SSO_ENTERPRISE_URL,
        json={
            'email': req.email,
            'password': decrypted_password
        }
    )
    if sso_res['code'] != 200:
        logger.info(f'企业账号:[ {req.email} ] 企业账号认证请求失败')
        raise ServiceError(sso_res['message'])
    logger.info(f'企业账号:[ {req.email} ] 企业账号认证成功')

    # 查询用户信息
    user = user_dao.select_by_email(req.email)
    user_no = user.USER_NO if user else new_id()

    # 用户不存在时新增
    sso_res_data = sso_res['data']
    if not user:
        logger.info(f'企业账号:[ {req.email} ] 平台用户信息不存在，创建用户并绑定默认角色')
        # 创建用户
        TUser.insert(
            USER_NO=user_no,
            USER_NAME=sso_res_data['username'],
            MOBILE=sso_res_data['mobile'],
            EMAIL=sso_res_data['email'],
            STATE='ENABLE',
            SSO=True,
            LOGGED_IN=True
        )
        # 绑定默认角色
        role = role_dao.select_by_code('DEFAULT')
        TUserRole.insert(
            USER_NO=user_no,
            ROLE_NO=role.ROLE_NO
        )
        # 创建个人空间
        workspace_no = new_id()
        TWorkspace.insert(
            WORKSPACE_NO=workspace_no,
            WORKSPACE_NAME='个人空间',
            WORKSPACE_SCOPE='PRIVATE'
        )
        TWorkspaceUser.insert(WORKSPACE_NO=workspace_no, USER_NO=user_no)
        # 创建空间变量
        TVariableDataset.insert(
            WORKSPACE_NO=workspace_no,
            DATASET_NO=new_id(),
            DATASET_NAME='空间变量',
            DATASET_TYPE=VariableDatasetWeight.WORKSPACE.name,
            DATASET_WEIGHT=VariableDatasetWeight.WORKSPACE.value
        )
    else:
        # 更新用户信息和登录状态
        kwargs = {'LOGGED_IN': True}
        if user.USER_NAME != sso_res_data['username']:
            kwargs['USER_NAME'] = sso_res_data['username']
        if user.MOBILE != sso_res_data['mobile']:
            kwargs['MOBILE'] = sso_res_data['mobile']
        if user.SSO is not True:
            kwargs['SSO'] = True
        user.update(**kwargs)

    # token签发时间
    issued_at = timestamp_now()

    # 记录用户登录日志
    TUserLoginLog.insert(
        USER_NO=user_no,
        LOGIN_NAME=req.email,
        LOGIN_TYPE='EMAIL',
        LOGIN_METHOD='ENTERPRISE',
        LOGIN_IP=remote_addr(),
        LOGIN_TIME=timestamp_to_utc8_datetime(issued_at)
    )

    # 生成access-token
    return {'accessToken': JWTAuth.encode_token(user_no, issued_at)}


def remote_addr():
    if x_forwarded_for := request.headers.get('X-Forwarded-For'):
        ip_list = x_forwarded_for.split(',')
        return ip_list[0]
    else:
        return request.remote_addr


@http_service
def logout():
    # 查询用户
    user = user_dao.select_by_no(localvars.get_user_no())
    check_exists(user, error_msg='用户不存在')
    # 登出
    user.update(LOGGED_IN=False)


@http_service
def register(req):
    ...


@http_service
def create_user(req):
    # 查询用户登录信息
    login_info = user_login_info_dao.select_by_loginname(req.loginName)
    check_not_exists(login_info, error_msg='登录账号已存在')

    # 查询用户
    user = user_dao.select_first(USER_NAME=req.userName, MOBILE=req.mobile, EMAIL=req.email)
    check_not_exists(user, error_msg='用户已存在')

    # 创建用户
    user_no = new_id()
    TUser.insert(
        USER_NO=user_no,
        USER_NAME=req.userName,
        MOBILE=req.mobile,
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
    workspace_no = new_id()
    TWorkspace.insert(
        WORKSPACE_NO=workspace_no,
        WORKSPACE_NAME='个人空间',
        WORKSPACE_SCOPE='PRIVATE'
    )
    TWorkspaceUser.insert(WORKSPACE_NO=workspace_no, USER_NO=user_no)

    # 创建空间变量
    TVariableDataset.insert(
        WORKSPACE_NO=workspace_no,
        DATASET_NO=new_id(),
        DATASET_NAME='空间变量',
        DATASET_TYPE=VariableDatasetWeight.WORKSPACE.name,
        DATASET_WEIGHT=VariableDatasetWeight.WORKSPACE.value
    )

    # 绑定用户角色
    if req.roles:
        for role_no in req.roles:
            TUserRole.insert(USER_NO=user_no, ROLE_NO=role_no)

    # 绑定用户分组
    if req.groups:
        for group_no in req.groups:
            TGroupMember.insert(USER_NO=user_no, GROUP_NO=group_no)


@http_service
def reset_login_password(req):
    # 查询用户
    user = user_dao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 查询登录信息
    login_info = user_login_info_dao.select_by_user(req.userNo)
    check_exists(login_info, error_msg='用户登录信息不存在')

    # 查询用户密码
    user_password = user_password_dao.select_loginpwd_by_user(req.userNo)
    check_exists(user_password, error_msg='用户登录密码不存在')

    # 更新用户密码
    user_password.update(PASSWORD=encrypt_password(login_info.LOGIN_NAME, '123456'))


@http_service
def query_user_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.add(TUser.DELETED == 0)
    conds.add(or_(TUserLoginInfo.DELETED == 0, TUserLoginInfo.DELETED.is_(None)))
    conds.add(or_(TUserLoginInfo.LOGIN_TYPE == 'ACCOUNT', TUserLoginInfo.LOGIN_TYPE.is_(None)))
    conds.notequal(TUser.USER_NO, '9999')
    conds.like(TUser.USER_NO, req.userNo)
    conds.like(TUser.USER_NAME, req.userName)
    conds.like(TUser.MOBILE, req.mobile)
    conds.like(TUser.EMAIL, req.email)
    conds.like(TUser.STATE, req.state)
    conds.equal(TUserLoginInfo.LOGIN_NAME, req.loginName)

    # 查询用户列表
    pagination = (
        db_query(
            TUser.USER_NO,
            TUser.USER_NAME,
            TUser.MOBILE,
            TUser.EMAIL,
            TUser.STATE,
            TUser.AVATAR,
            TUser.SSO,
            TUserLoginInfo.LOGIN_NAME
        )
        .outerjoin(TUserLoginInfo, TUserLoginInfo.USER_NO == TUser.USER_NO)
        .filter(*conds)
        .order_by(TUser.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = []
    for user in pagination.items:
        # 跳过 administrator 用户
        if user.LOGIN_NAME == 'admin':
            continue
        # 查询用户绑定的角色列表
        roles = []
        user_roles = user_role_dao.select_all_by_userno(user.USER_NO)
        for user_role in user_roles:
            if role := role_dao.select_by_no(user_role.ROLE_NO):
                roles.append({
                    'roleNo': role.ROLE_NO,
                    'roleName': role.ROLE_NAME
                })
        # 查询用户分组列表
        groups = []
        user_groups = group_member_dao.select_all_by_user(user.USER_NO)
        for user_group in user_groups:
            if group := group_dao.select_by_no(user_group.GROUP_NO):
                groups.append({
                    'groupNo': group.GROUP_NO,
                    'groupName': group.GROUP_NAME
                })

        data.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'loginName': user.LOGIN_NAME,
            'avatar': user.AVATAR,
            'mobile': user.MOBILE,
            'email': user.EMAIL,
            'state': user.STATE,
            'sso': user.SSO,
            'roles': roles,
            'groups': groups
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_user_all():
    # 查询条件
    conds = QueryCondition()
    conds.add(TUser.DELETED == 0)
    conds.add(or_(TUserLoginInfo.DELETED == 0, TUserLoginInfo.DELETED.is_(None)))
    conds.add(or_(TUserLoginInfo.LOGIN_TYPE == 'ACCOUNT', TUserLoginInfo.LOGIN_TYPE.is_(None)))
    conds.notequal(TUser.USER_NO, '9999')

    # 查询用户列表
    users = (
        db_query(
            TUser.USER_NO,
            TUser.USER_NAME,
            TUser.STATE,
            TUserLoginInfo.LOGIN_NAME
        )
        .outerjoin(TUserLoginInfo, TUserLoginInfo.USER_NO == TUser.USER_NO)
        .filter(*conds)
        .order_by(TUser.CREATED_TIME.desc())
        .all()
    )

    return [
        {
            'userNo': user.USER_NO,
            'userName': user.USER_NAME,
            'state': user.STATE
        }
        for user in users if user.LOGIN_NAME != 'admin'
    ]


def get_user_roles(user_no):
    # 用户角色
    user_role_conds = QueryCondition(TRole, TUserRole)
    user_role_conds.equal(TUserRole.USER_NO, user_no)
    user_role_conds.equal(TUserRole.ROLE_NO, TRole.ROLE_NO)
    user_role_stmt = db_query(TRole.ROLE_CODE).filter(*user_role_conds)
    # 分组角色
    group_role_conds = QueryCondition(TGroup, TRole, TGroupMember, TGroupRole)
    group_role_conds.equal(TGroupMember.USER_NO, user_no)
    group_role_conds.equal(TGroupMember.GROUP_NO, TGroup.GROUP_NO)
    group_role_conds.equal(TGroupRole.ROLE_NO, TRole.ROLE_NO)
    group_role_conds.equal(TGroupRole.GROUP_NO, TGroupMember.GROUP_NO)
    group_role_stmt = db_query(TRole.ROLE_CODE).filter(*group_role_conds)
    # 连表查询
    return user_role_stmt.union(group_role_stmt).all()


@http_service
def query_user_info():
    # 获取用户编号
    user_no = localvars.get_user_no()
    # 查询用户
    user = user_dao.select_by_no(user_no)
    # 查询用户角色
    roles = [role.ROLE_CODE for role in get_user_roles(user_no)]

    return {
        'userNo': user_no,
        'userName': user.USER_NAME,
        'avatar': user.AVATAR,
        'mobile': user.MOBILE,
        'email': user.EMAIL,
        'sso': user.SSO,
        'roles': roles,
        'settings': user.SETTINGS or {}
    }


@http_service
def modify_user_info(req):
    # 获取用户编号
    user_no = localvars.get_user_no()
    # 查询用户
    user = user_dao.select_by_no(user_no)
    check_exists(user, error_msg='用户不存在')
    # 更新用户登录信息
    update_user_mobile_login_info(user_no, user.MOBILE, req.mobile)
    update_user_email_login_info(user_no, user.EMAIL, req.email)
    # 更新用户信息
    user.update(
        USER_NAME=req.userName,
        MOBILE=req.mobile,
        EMAIL=req.email
    )


def update_user_mobile_login_info(user_no, old_mobile, new_mobile):
    # 新手机号为空时无需处理
    if new_mobile is None:
        return
    # 查询旧手机号登录信息
    old_login_info = user_login_info_dao.select_by_loginname(old_mobile)
    if new_mobile:
        # 新旧手机号一致时无需处理
        if new_mobile == old_mobile:
            return
        # 判断新手机号是否存在
        new_login_info = user_login_info_dao.select_by_loginname(new_mobile)
        check_not_exists(new_login_info, error_msg='手机号已存在')
        # 更新或插入手机号登录方式
        if old_login_info:
            old_login_info.update(LOGIN_NAME=new_mobile)
        else:
            TUserLoginInfo.insert(
                USER_NO=user_no,
                LOGIN_NAME=new_mobile,
                LOGIN_TYPE='MOBILE'
            )
    else:
        # 新手机号为空时删除手机号登录方式
        old_login_info and old_login_info.delete()


def update_user_email_login_info(user_no, old_email, new_email):
    # 新邮箱为空时无需处理
    if new_email is None:
        return
    # 查询旧邮箱登录信息
    old_login_info = user_login_info_dao.select_by_loginname(old_email)
    if new_email:
        # 新旧邮箱一致时无需处理
        if new_email == old_email:
            return
        # 判断新邮箱是否存在
        new_login_info = user_login_info_dao.select_by_loginname(new_email)
        check_not_exists(new_login_info, error_msg='邮箱已存在')
        # 更新或插入邮箱登录方式
        if old_login_info:
            old_login_info.update(LOGIN_NAME=new_email)
        else:
            TUserLoginInfo.insert(
                USER_NO=user_no,
                LOGIN_NAME=new_email,
                LOGIN_TYPE='EMAIL'
            )
    else:
        # 新邮箱为空时删除邮箱登录方式
        old_login_info and old_login_info.delete()


@http_service
def modify_user_settings(req):
    # 获取用户编号
    user_no = localvars.get_user_no()
    # 查询用户
    user = user_dao.select_by_no(user_no)
    check_exists(user, error_msg='用户不存在')
    # 更新用户设置
    user.update(SETTINGS=req.data)


@http_service
def modify_user_password(req):
    try:
        # 获取用户编号
        user_no = localvars.get_user_no()
        # 查询用户登录信息
        login_info = user_login_info_dao.select_by_user(user_no)
        check_exists(login_info, error_msg='用户登录信息不存在')
        # 查询用户密码
        login_password = user_password_dao.select_loginpwd_by_user(user_no)
        check_exists(login_password, error_msg='账号或密码不正确')
        # 查询密钥
        secret_key = cache.encryption_factors.get(req.index)
        if not secret_key:
            raise ServiceError('加密因子不存在')
        # 解密旧密码
        old_decrypted_password = decrypt_by_rsa_private_key(req.oldPassword, secret_key)
        # 校验密码是否正确
        password_success = check_password(login_info.LOGIN_NAME, login_password.PASSWORD, old_decrypted_password)
        # 密码校验失败
        if not password_success:
            logger.info('密码校验失败')
            login_password.LAST_FAILURE_TIME = datetime.now(UTC)
            if login_password.ERROR_TIMES < 3:
                logger.info('密码错误次数+1')
                login_password.ERROR_TIMES += 1
            raise ServiceError('账号或密码不正确')
        # 解密新密码
        new_decrypted_password = decrypt_by_rsa_private_key(req.newPassword, secret_key.DATA)
        # 更新用户登录密码
        login_password.update(PASSWORD=encrypt_password(login_info.LOGIN_NAME, new_decrypted_password))
        # 查询用户
        user = user_dao.select_by_no(user_no)
        # 登出
        user.update(LOGGED_IN=False)
    except Exception:
        raise
    finally:
        # 删除密钥索引
        cache.encryption_factors.pop(req.index)


@http_service
def modify_user(req):
    # 查询用户
    user = user_dao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')
    # 更新用户登录信息
    update_user_mobile_login_info(req.userNo, user.MOBILE, req.mobile)
    update_user_email_login_info(req.userNo, user.EMAIL, req.email)
    # 更新用户信息
    user.update(
        USER_NAME=req.userName,
        MOBILE=req.mobile,
        EMAIL=req.email
    )
    # 绑定用户角色
    update_user_roles(req.userNo, req.roles)
    # 绑定用户分组
    update_user_groups(req.userNo, req.groups)


def update_user_roles(user_no, roles):
    if roles is None:
        return
    # 批量绑定用户角色
    for role_no in roles:
        # 查询用户角色
        user_role = user_role_dao.select_by_user_and_role(user_no, role_no)
        if not user_role:
            TUserRole.insert(USER_NO=user_no, ROLE_NO=role_no)

    # 删除不在请求中的角色
    user_role_dao.delete_all_by_user_and_notin_role(user_no, roles)


def update_user_groups(user_no, groups):
    if groups is None:
        return
    # 批量绑定用户分组
    for group_no in groups:
        # 查询用户分组
        group_user = group_member_dao.select_by_user_and_group(user_no, group_no)
        if not group_user:
            TGroupMember.insert(USER_NO=user_no, GROUP_NO=group_no)

    # 解绑不在请求中的分组
    group_member_dao.delete_all_by_user_and_notin_group(user_no, groups)


def get_private_workspace_by_user(user_no):
    # 查询条件
    conds = QueryCondition(TWorkspace, TWorkspaceUser)
    conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    conds.equal(TWorkspace.WORKSPACE_SCOPE, 'PRIVATE')
    conds.equal(TWorkspaceUser.USER_NO, user_no)

    # 查询私人空间
    return db_query(TWorkspace).filter(*conds).first()


@http_service
def modify_user_state(req):
    # 查询用户
    user = user_dao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 更新用户状态
    user.update(STATE=req.state)


@http_service
def remove_user(req):
    # 查询用户
    user = user_dao.select_by_no(req.userNo)
    check_exists(user, error_msg='用户不存在')

    # 删除用户角色
    user_role_dao.delete_all_by_user(req.userNo)

    # 删除用户分组
    group_member_dao.delete_all_by_user(req.userNo)

    # 删除用户密码
    user_password_dao.delete_all_by_user(req.userNo)

    # 删除用户登录账号
    user_login_info_dao.delete_all_by_user(req.userNo)

    # 删除私人空间
    workspace = get_private_workspace_by_user(req.userNo)
    workspace.delete()

    # 删除空间成员
    TWorkspaceUser.deletes(TWorkspaceUser.USER_NO == req.userNo)

    # 删除用户
    user.delete()
