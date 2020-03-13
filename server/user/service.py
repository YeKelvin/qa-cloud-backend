#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from datetime import datetime

from server.librarys.decorators.service import http_service
from server.librarys.exception import ServiceError
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.verify import Verify
from server.user.model import TUser, TUserRoleRel, TRole, TPermission, TRolePermissionRel
from server.user.utils.auth import Auth
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def login(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.not_empty(user, '账号或密码不正确')

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
    user.update(
        access_token=token,
        last_login_time=login_time,
        last_success_time=login_time,
        error_times=0
    )
    # 记录操作员，用于记录操作日志表
    Global.set('operator', user.username)
    return {'accessToken': token}


@http_service
def logout():
    user = Global.user
    user.access_token = ''
    user.updated_by = user.username
    user.save()
    return None


@http_service
def register(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.empty(user, '该用户名称已存在')

    # 创建用户
    user_no = generate_user_no()
    TUser.create(
        user_no=user_no,
        username=req.attr.username,
        nickname=req.attr.nickname,
        password=req.attr.password,
        mobile_no=req.attr.mobileNo,
        email=req.attr.email,
        state='NORMAL',
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def reset_password(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    user.password = '123456'
    user.save()
    return None


@http_service
def user_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

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

    # 列表总数
    total_size = TUser.query.filter(*conditions).count()
    # 列表数据
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
def user_all():
    users = TUser.query.order_by(TUser.created_time.desc()).all()
    result = []
    for user in users:
        result.append({
            'userNo': user.user_no,
            'username': user.username
        })
    return result


@http_service
def user_info():
    user = Global.user
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
def modify_user(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    if req.attr.username:
        user.username = req.attr.username
    if req.attr.nickname:
        user.nickname = req.attr.nickname
    if req.attr.mobileNo:
        user.mobile_no = req.attr.mobileNo
    if req.attr.email:
        user.email = req.attr.email
    user.save()
    return None


@http_service
def modify_user_state(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    user.update(state=req.attr.state)
    return None


@http_service
def delete_user(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    # 删除用户角色关联关系
    user_roles = TUserRoleRel.query.filter_by(user_no=req.attr.userNo).all()
    for user_role in user_roles:
        user_role.delete()

    # 删除用户
    user.delete()
    return None


@http_service
def permission_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

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

    # 列表总数
    total_size = TPermission.query.filter(*conditions).count()
    # 列表数据
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
def permission_all():
    permissions = TPermission.query.order_by(TPermission.created_time.desc()).all()
    result = []
    for permission in permissions:
        result.append({
            'permissionNo': permission.permission_no,
            'permissionName': permission.permission_name,
            'endpoint': permission.endpoint,
            'method': permission.method,
            'state': permission.state
        })
    return result


@http_service
def create_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(endpoint=req.attr.endpoint, method=req.attr.method).first()
    Verify.empty(permission, '权限已存在')

    TPermission.create(
        permission_no=generate_permission_no(),
        permission_name=req.attr.permissionName,
        endpoint=req.attr.endpoint,
        method=req.attr.method,
        state='NORMAL',
        description=req.attr.description,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def modify_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

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
def modify_permission_state(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    permission.update(state=req.attr.state)
    return None


@http_service
def delete_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    permission.delete()
    return None


@http_service
def role_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.roleNo:
        conditions.append(TRole.role_no.like(f'%{req.attr.roleNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.role_name.like(f'%{req.attr.roleName}%'))
    if req.attr.state:
        conditions.append(TRole.state == req.attr.state)
    if req.attr.description:
        conditions.append(TRole.description.like(f'%{req.attr.description}%'))

    # 列表总数
    total_size = TRole.query.filter(*conditions).count()
    # 列表数据
    roles = TRole.query.filter(*conditions).order_by(TRole.created_time.desc()).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for role in roles:
        data_set.append({
            'roleNo': role.role_no,
            'roleName': role.role_name,
            'state': role.state,
            'description': role.description
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def role_all():
    roles = TRole.query.order_by(TRole.created_time.desc()).all()
    result = []
    for role in roles:
        result.append({
            'roleNo': role.role_no,
            'roleName': role.role_name,
            'state': role.state,
            'description': role.description
        })
    return result


@http_service
def create_role(req: RequestDTO):
    role = TRole.query.filter_by(role_name=req.attr.roleName).first()
    Verify.empty(role, '角色已存在')

    TRole.create(
        role_no=generate_role_no(),
        role_name=req.attr.roleName,
        state='NORMAL',
        description=req.attr.description,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def modify_role(req: RequestDTO):
    role = TRole.query.filter_by(role_no=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    if req.attr.roleName:
        role.role_name = req.attr.roleName
    if req.attr.description:
        role.description = req.attr.description
    role.save()
    return None


@http_service
def modify_role_state(req: RequestDTO):
    role = TRole.query.filter_by(role_no=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    role.update(state=req.attr.state)
    return None


@http_service
def delete_role(req: RequestDTO):
    role = TRole.query.filter_by(role_no=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    user_roles = TUserRoleRel.query.filter_by(role_no=req.attr.roleNo).all()
    Verify.empty(user_roles, '角色与用户存在关联关系，请先解除关联')

    # 删除角色权限关联关系
    role_permissions = TRolePermissionRel.query.filter_by(role_no=req.attr.roleNo).all()
    for role_permission in role_permissions:
        role_permission.delete()

    # 删除角色
    role.delete()
    return None


@http_service
def user_role_rel_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    # TUserRoleRel查询条件
    if req.attr.userNo:
        conditions.append(TUserRoleRel.user_no.like(f'%{req.attr.userNo}%'))
    if req.attr.roleNo:
        conditions.append(TUserRoleRel.role_no.like(f'%{req.attr.roleNo}%'))
    # TRole查询条件
    if req.attr.roleName:
        conditions.append(TRole.role_name.like(f'%{req.attr.roleName}%'))
    # TUser查询条件
    if req.attr.username:
        conditions.append(TUser.username.like(f'%{req.attr.username}%'))

    # 列表总数
    total_size = TUserRoleRel.query.join(
        TRole, TUserRoleRel.role_no == TRole.role_no
    ).join(
        TUser, TUserRoleRel.user_no == TUser.user_no
    ).filter(
        *conditions
    ).count()

    # 列表数据
    querys = TUserRoleRel.query.with_entities(
        TUserRoleRel.user_no,
        TUserRoleRel.role_no,
        TRole.role_name,
        TUser.username,
        TUserRoleRel.created_time
    ).join(
        TRole, TUserRoleRel.role_no == TRole.role_no
    ).join(
        TUser, TUserRoleRel.user_no == TUser.user_no
    ).filter(
        *conditions
    ).order_by(
        TUserRoleRel.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for query in querys:
        data_set.append({
            'userNo': query.user_no,
            'roleNo': query.role_no,
            'username': query.username,
            'roleName': query.role_name,
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query.filter_by(
        user_no=req.attr.userNo,
        role_no=req.attr.roleNo
    ).first()
    Verify.empty(user_role, '用户角色关联关系已存在')

    TUserRoleRel.create(
        user_no=req.attr.userNo,
        role_no=req.attr.roleNo,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def delete_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query.filter_by(
        user_no=req.attr.userNo,
        role_no=req.attr.roleNo
    ).first()
    Verify.not_empty(user_role, '用户角色关联关系不存在')

    user_role.delete()
    return None


@http_service
def role_permission_rel_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    # TRolePermissionRel查询条件
    if req.attr.roleNo:
        conditions.append(TRolePermissionRel.role_no.like(f'%{req.attr.roleNo}%'))
    if req.attr.permissionNo:
        conditions.append(TRolePermissionRel.permission_no.like(f'%{req.attr.permissionNo}%'))
    # TRole查询条件
    if req.attr.roleName:
        conditions.append(TRole.role_name.like(f'%{req.attr.roleName}%'))
    # TPermission查询条件
    if req.attr.permissionName:
        conditions.append(TPermission.permission_name.like(f'%{req.attr.permissionName}%'))
    if req.attr.endpoint:
        conditions.append(TPermission.endpoint.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        conditions.append(TPermission.method.like(f'%{req.attr.method}%'))

    # 列表总数
    total_size = TRolePermissionRel.query.join(
        TRole, TRolePermissionRel.role_no == TRole.role_no
    ).join(
        TPermission, TRolePermissionRel.permission_no == TPermission.permission_no
    ).filter(
        *conditions
    ).count()

    # 列表数据
    querys = TRolePermissionRel.query.with_entities(
        TRolePermissionRel.role_no,
        TRolePermissionRel.permission_no,
        TRole.role_name,
        TPermission.permission_name,
        TPermission.endpoint,
        TPermission.method,
        TRolePermissionRel.created_time
    ).join(
        TRole, TRolePermissionRel.role_no == TRole.role_no
    ).join(
        TPermission, TRolePermissionRel.permission_no == TPermission.permission_no
    ).filter(
        *conditions
    ).order_by(
        TRolePermissionRel.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for query in querys:
        data_set.append({
            'roleNo': query.role_no,
            'roleName': query.role_name,
            'permissionNo': query.permission_no,
            'permissionName': query.permission_name,
            'endpoint': query.endpoint,
            'method': query.method
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query.filter_by(
        role_no=req.attr.roleNo,
        permission_no=req.attr.permissionNo
    ).first()
    Verify.empty(role_permission, '角色权限关联关系已存在')

    TRolePermissionRel.create(
        role_no=req.attr.roleNo,
        permission_no=req.attr.permissionNo,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def delete_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query.filter_by(
        role_no=req.attr.roleNo,
        permission_no=req.attr.permissionNo
    ).first()
    Verify.not_empty(role_permission, '角色权限关联关系不存在')

    role_permission.delete()
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
