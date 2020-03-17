#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from server.librarys.decorators.service import http_service
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.verify import Verify
from server.user.model import TUser, TUserRoleRel, TRole, TPermission, TRolePermissionRel
from server.utils.log_util import get_logger

log = get_logger(__name__)


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

    if req.attr.roleName is not None:
        role.role_name = req.attr.roleName
    if req.attr.description is not None:
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


def generate_role_no():
    """生成角色编号
    """
    seq_role_no = Sequence('seq_role_no')
    return 'R' + str(seq_role_no.next_value()).zfill(10)
