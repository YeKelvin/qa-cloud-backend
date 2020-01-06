#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from datetime import datetime

from flask import g

from server.librarys.decorators import http_service
from server.librarys.exception import ServiceError
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.sqlalchemy_helper import get_page_number_info
from server.librarys.verify import Verify
from server.user.auth import Auth
from server.user.model import TUser, TUserRoleRel, TRole, TPermission, TRolePermissionRel
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def register(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.is_empty(user, '该用户名称已存在')

    TUser.create(
        user_no=generate_user_no(),
        username=req.attr.username,
        nickname=req.attr.nickname,
        password=req.attr.password,
        mobile_no=req.attr.mobileNo,
        email=req.attr.email,
        state='NORMAL',
        created_time=datetime.now(),
        created_by=getattr(g, 'operator', None),
        updated_by=getattr(g, 'operator', None)
    )
    return None


@http_service
def modify_user(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.is_not_empty(user, '用户不存在')
    return None


@http_service
def delete_user(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.is_not_empty(user, '用户不存在')
    return None


@http_service
def login(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.is_not_empty(user, '账号或密码不正确')

    # 密码校验失败
    if not user.check_password_hash(req.attr.password):
        user.last_error_time = datetime.utcnow()
        if user.error_times < 3:
            user.error_times += 1
        user.save()
        raise ServiceError('账号或密码不正确')

    # 密码校验通过
    login_time = datetime.utcnow()
    token = Auth.encode_auth_token(user.user_no, login_time.timestamp())
    user.update(access_token=token, last_login_time=login_time, last_success_time=login_time, error_times=0)
    # 记录操作员，用于记录操作日志表
    g.operator = user.username
    return {'accessToken': token}


@http_service
def logout():
    user = getattr(g, 'user', None)
    user.access_token = ''
    user.updated_by = user.username
    return None


@http_service
def user_info():
    user = getattr(g, 'user', None)
    user_roles = TUserRoleRel.query.filter_by(user_no=user.user_no).all()
    roles = []
    for user_role in user_roles:
        role = TRole.query.filter_by(role_no=user_role.role_no).first()
        roles.append(role.role_name)
    return {
        'userNo': user.user_no,
        'userName': user.username,
        'nickName': user.nickname,
        'mobileNo': user.mobile_no,
        'email': user.email,
        'avatar': user.avatar,
        'roles': roles
    }


@http_service
def user_list(req: RequestDTO):
    # 分页
    offset, limit = get_page_number_info(req)

    # 查询条件
    conditions = []
    if req.attr.userNo:
        conditions.append(TUser.user_no == req.attr.userNo)
    if req.attr.username:
        conditions.append(TUser.username.like(f'%{req.attr.username}%'))
    if req.attr.nickname:
        conditions.append(TUser.nickname.like(f'%{req.attr.nickname}%'))
    if req.attr.mobileNo:
        conditions.append(TUser.mobile_no.like(f'%{req.attr.mobileNo}%'))
    if req.attr.email:
        conditions.append(TUser.email.like(f'%{req.attr.email}%'))
    if req.attr.state:
        conditions.append(TUser.state.like(f'%{req.attr.state}%'))

    total_size = TUser.query.filter(*conditions).count()
    users = TUser.query.filter(*conditions).order_by(TUser.created_time.desc()).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for user in users:
        user_roles = TUserRoleRel.query.filter_by(user_no=user.user_no).all()
        roles = []
        for user_role in user_roles:
            role = TRole.query.filter_by(role_no=user_role.role_no).first()
            roles.append(role.role_name)
        data_set.append({
            'userNo': user.user_no,
            'username': user.username,
            'nickname': user.nickname,
            'mobileNo': user.mobile_no,
            'email': user.email,
            'state': user.state,
            'roles': roles
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def role_permission_rel_list(req: RequestDTO):
    # 分页
    offset, limit = get_page_number_info(req)

    # TRole 查询条件
    role_conditions = []
    if req.attr.roleName:
        role_conditions.append(TRole.role_name.like(f'%{req.attr.roleName}%'))
    roles = TRole.query.filter(*role_conditions).all()

    # role_no in 查询条件
    role_no_list = []
    for role in roles:
        role_no_list.append(role.role_no)

    # TPermission 查询条件
    permission_conditions = []
    if req.attr.permissionName:
        permission_conditions.append(TPermission.permission_name.like(f'%{req.attr.permissionName}%'))
    if req.attr.endpoint:
        permission_conditions.append(TPermission.endpoint.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        permission_conditions.append(TPermission.method.like(f'%{req.attr.method}%'))
    if req.attr.state:
        permission_conditions.append(TPermission.state.like(f'%{req.attr.state}%'))

    total_size = TRolePermissionRel.join(
        TPermission, TRolePermissionRel.permission_no == TPermission.permission_no
    ).filter(
        TRolePermissionRel.role_no.in_(role_no_list)
    ).filter(
        *permission_conditions
    ).count()

    role_permissions = TRolePermissionRel.join(
        TPermission, TRolePermissionRel.permission_no == TPermission.permission_no
    ).filter(
        TRolePermissionRel.role_no.in_(role_no_list)
    ).filter(
        *permission_conditions
    ).order_by(
        TRolePermissionRel.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for role_permission in role_permissions:
        role_name = None
        for role in role_list:
            if role_permission.role_no == role.role_no:
                role_name = role.role_name
        data_set.append({
            'roleNo': role_permission.role_no,
            'roleName': role_name,
            'permissionNo': role_permission.permission_no,
            'permissionName': role_permission.permission_name,
            'endpoint': role_permission.endpoint,
            'method': role_permission.method,
            'state': role_permission.state
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_role_permission_rel(req: RequestDTO):
    role_permission_rel = TRolePermissionRel.query.filter_by(
        role_no=req.attr.roleNo,
        permission_no=req.attr.permissionNo
    ).first()
    Verify.is_empty(role_permission_rel, '角色权限关系已存在')

    return None


@http_service
def modify_role_permission_rel(req: RequestDTO):
    role_permission_rel = TRolePermissionRel.query.filter_by(
        role_no=req.attr.roleNo,
        permission_no=req.attr.permissionNo
    ).first()
    Verify.is_not_empty(role_permission_rel, '角色权限关系不存在')

    role_permission_rel.save()
    return None


@http_service
def delete_role_permission_rel(req: RequestDTO):
    role_permission_rel = TRolePermissionRel.query.filter_by(
        role_no=req.attr.roleNo,
        permission_no=req.attr.permissionNo
    ).first()
    Verify.is_not_empty(role_permission_rel, '角色权限关系不存在')

    role_permission_rel.deltet()
    return None


@http_service
def permission_list(req: RequestDTO):
    # 分页
    offset, limit = get_page_number_info(req)

    # 查询条件
    conditions = []
    if req.attr.permissionNo:
        conditions.append(TPermission.permission_no == req.attr.permissionNo)
    if req.attr.permissionName:
        conditions.append(TPermission.permission_name.like(f'%{req.attr.permissionName}%'))
    if req.attr.endpoint:
        conditions.append(TPermission.endpoint.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        conditions.append(TPermission.method.like(f'%{req.attr.method}%'))
    if req.attr.state:
        conditions.append(TPermission.state.like(f'%{req.attr.state}%'))

    total_size = TPermission.query.filter(*conditions).count()
    permissions = TPermission.query.filter(
        *conditions
    ).order_by(
        TPermission.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for permission in permissions:
        data_set.append({
            'permissionNo': permission.permission_no,
            'permissionName': permission.permission_name,
            'endpoint': permission.endpoint,
            'method': permission.method,
            'state': permission.state
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(endpoint=req.attr.endpoint).first()
    Verify.is_empty(permission, '权限已存在')

    TPermission.create(
        permission_no=generate_permission_no(),
        permission_name=req.attr.permissionName,
        endpoint=req.attr.endpoint,
        method=req.attr.method,
        state='NORMAL',
        remark=req.attr.remark,
        created_time=datetime.now(),
        created_by=getattr(g, 'operator', None),
        updated_time=datetime.now(),
        updated_by=getattr(g, 'operator', None)
    )
    return None


@http_service
def modify_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.is_not_empty(permission, '权限不存在')

    if req.attr.permissionNo:
        permission.permission_no = req.attr.permissionNo
    if req.attr.permissionName:
        permission.permission_name = req.attr.permissionName
    if req.attr.endpoint:
        permission.endpoint = req.attr.endpoint
    if req.attr.method:
        permission.method = req.attr.method
    permission.save()
    return None


@http_service
def delete_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.is_not_empty(permission, '权限不存在')

    permission.delete()
    return None


@http_service
def role_list(req: RequestDTO):
    # 分页
    offset, limit = get_page_number_info(req)

    # 查询条件
    conditions = []
    if req.attr.roleName:
        conditions.append(TRole.role_name.like(f'%{req.attr.roleName}%'))

    total_size = TRole.query.filter(*conditions).count()
    roles = TRole.query.filter(*conditions).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for role in roles:
        data_set.append({
            'roleNo': role.role_no,
            'roleName': role.role_name,
            'remark': role.remark
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_role(req: RequestDTO):
    role = TRole.query.filter_by(role_name=req.attr.roleName).first()
    Verify.is_empty(role, '角色已存在')

    TRole.create(
        role_no=generate_role_no(),
        role_name=req.attr.roleName,
        state='NORMAL',
        remark=req.attr.remark,
        created_time=datetime.now(),
        created_by=getattr(g, 'operator', None),
        updated_time=datetime.now(),
        updated_by=getattr(g, 'operator', None)
    )
    return None


@http_service
def modify_role(req: RequestDTO):
    role = TRole.query.filter_by(role_no=req.attr.roleNo).first()
    Verify.is_not_empty(role, '角色不存在')

    if req.attr.roleName:
        role.role_name = req.attr.roleName
    if req.attr.remark:
        role.remark = req.attr.remark
    role.save()
    return None


@http_service
def delete_role(req: RequestDTO):
    role = TRole.query.filter_by(role_no=req.attr.roleNo).first()
    Verify.is_not_empty(role, '角色不存在')

    role.delete()
    return None


def generate_user_no():
    """生成用户编号
    """
    seq_user_no = Sequence('seq_user_no')
    return 'U' + str(seq_user_no.next_value()).zfill(8)


def generate_role_no():
    """生成角色编号
    """
    seq_role_no = Sequence('seq_role_no')
    return 'R' + str(seq_role_no.next_value()).zfill(8)


def generate_permission_no():
    """生成权限编号
    """
    seq_permission_no = Sequence('seq_permission_no')
    return 'P' + str(seq_permission_no.next_value()).zfill(8)
