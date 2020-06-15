#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from server.common.number_generator import generate_role_no
from server.librarys.decorators.service import http_service
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.user.model import TUser, TUserRoleRel, TRole, TPermission, TRolePermissionRel
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_role_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.roleNo:
        conditions.append(TRole.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    if req.attr.roleDesc:
        conditions.append(TRole.ROLE_DESC.like(f'%{req.attr.roleDesc}%'))
    if req.attr.state:
        conditions.append(TRole.STATE.like(f'%{req.attr.state}%'))

    # 列表总数
    total_size = TRole.query.filter(*conditions).count()
    # 列表数据
    roles = TRole.query.filter(*conditions).order_by(TRole.CREATED_TIME.desc()).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for role in roles:
        data_set.append({
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleDesc': role.ROLE_DESC,
            'state': role.STATE
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_role_all():
    roles = TRole.query.order_by(TRole.CREATED_TIME.desc()).all()
    result = []
    for role in roles:
        result.append({
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleDesc': role.ROLE_DESC,
            'state': role.STATE
        })
    return result


@http_service
def create_role(req: RequestDTO):
    role = TRole.query.filter_by(ROLE_NAME=req.attr.roleName).first()
    Verify.empty(role, '角色已存在')

    TRole.create(
        ROLE_NO=generate_role_no(),
        ROLE_NAME=req.attr.roleName,
        ROLE_DESC=req.attr.roleDesc,
        STATE='ENABLE',
        CREATED_BY=Global.operator,
        CREATED_TIME=datetime.now(),
        UPDATED_BY=Global.operator,
        UPDATED_TIME=datetime.now()
    )
    return None


@http_service
def modify_role(req: RequestDTO):
    role = TRole.query.filter_by(ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    if req.attr.roleName is not None:
        role.ROLE_NAME = req.attr.roleName
    if req.attr.roleDesc is not None:
        role.ROLE_DESC = req.attr.roleDesc

    role.save()
    return None


@http_service
def modify_role_state(req: RequestDTO):
    role = TRole.query.filter_by(ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    role.update(STATE=req.attr.state)
    return None


@http_service
def delete_role(req: RequestDTO):
    role = TRole.query.filter_by(ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    user_roles = TUserRoleRel.query.filter_by(ROLE_NO=req.attr.roleNo).all()
    Verify.empty(user_roles, '角色与用户存在关联关系，请先解除关联')

    # 删除角色权限关联关系
    role_permissions = TRolePermissionRel.query.filter_by(ROLE_NO=req.attr.roleNo).all()
    for role_permission in role_permissions:
        role_permission.delete()

    # 删除角色
    role.delete()
    return None


@http_service
def query_user_role_rel_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    # TUserRoleRel查询条件
    if req.attr.userNo:
        conditions.append(TUserRoleRel.USER_NO.like(f'%{req.attr.userNo}%'))
    if req.attr.roleNo:
        conditions.append(TUserRoleRel.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    # TRole查询条件
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    # TUser查询条件
    if req.attr.username:
        conditions.append(TUser.USER_NAME.like(f'%{req.attr.username}%'))

    # 列表总数
    total_size = TUserRoleRel.query.join(
        TRole, TUserRoleRel.ROLE_NO == TRole.ROLE_NO
    ).join(
        TUser, TUserRoleRel.USER_NO == TUser.USER_NO
    ).filter(
        *conditions
    ).count()

    # 列表数据
    querys = TUserRoleRel.query.with_entities(
        TUserRoleRel.USER_NO,
        TUserRoleRel.ROLE_NO,
        TRole.ROLE_NAME,
        TUser.USER_NAME,
        TUserRoleRel.CREATED_TIME
    ).join(
        TRole, TUserRoleRel.ROLE_NO == TRole.ROLE_NO
    ).join(
        TUser, TUserRoleRel.USER_NO == TUser.USER_NO
    ).filter(
        *conditions
    ).order_by(
        TUserRoleRel.CREATED_TIME.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for query in querys:
        data_set.append({
            'userNo': query.USER_NO,
            'roleNo': query.ROLE_NO,
            'userName': query.USER_NAME,
            'roleName': query.ROLE_NAME,
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query.filter_by(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo).first()
    Verify.empty(user_role, '用户角色关联关系已存在')

    TUserRoleRel.create(
        USER_NO=req.attr.userNo,
        ROLE_NO=req.attr.roleNo,
        CREATED_BY=Global.operator,
        CREATED_TIME=datetime.now(),
        UPDATED_BY=Global.operator,
        UPDATED_TIME=datetime.now()
    )
    return None


@http_service
def delete_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query.filter_by(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(user_role, '用户角色关联关系不存在')

    user_role.delete()
    return None


@http_service
def query_role_permission_rel_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    # TRolePermissionRel查询条件
    if req.attr.roleNo:
        conditions.append(TRolePermissionRel.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.permissionNo:
        conditions.append(TRolePermissionRel.PERMISSION_NO.like(f'%{req.attr.permissionNo}%'))
    # TRole查询条件
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    # TPermission查询条件
    if req.attr.permissionName:
        conditions.append(TPermission.PERMISSION_NAME.like(f'%{req.attr.permissionName}%'))
    if req.attr.endpoint:
        conditions.append(TPermission.ENDPOINT.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        conditions.append(TPermission.METHOD.like(f'%{req.attr.method}%'))

    # 列表总数
    total_size = TRolePermissionRel.query.join(
        TRole, TRolePermissionRel.ROLE_NO == TRole.ROLE_NO
    ).join(
        TPermission, TRolePermissionRel.PERMISSION_NO == TPermission.PERMISSION_NO
    ).filter(
        *conditions
    ).count()

    # 列表数据
    querys = TRolePermissionRel.query.with_entities(
        TRolePermissionRel.ROLE_NO,
        TRolePermissionRel.PERMISSION_NO,
        TRole.ROLE_NAME,
        TPermission.PERMISSION_NAME,
        TPermission.ENDPOINT,
        TPermission.METHOD,
        TRolePermissionRel.CREATED_TIME
    ).join(
        TRole, TRolePermissionRel.ROLE_NO == TRole.ROLE_NO
    ).join(
        TPermission, TRolePermissionRel.PERMISSION_NO == TPermission.PERMISSION_NO
    ).filter(
        *conditions
    ).order_by(
        TRolePermissionRel.CREATED_TIME.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for query in querys:
        data_set.append({
            'roleNo': query.ROLE_NO,
            'roleName': query.ROLE_NAME,
            'permissionNo': query.PERMISSION_NO,
            'permissionName': query.PERMISSION_NAME,
            'endpoint': query.ENDPOINT,
            'method': query.METHOD
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def create_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query.filter_by(
        ROLE_NO=req.attr.roleNo,
        PERMISSION_NO=req.attr.permissionNo
    ).first()
    Verify.empty(role_permission, '角色权限关联关系已存在')

    TRolePermissionRel.create(
        ROLE_NO=req.attr.roleNo,
        PERMISSION_NO=req.attr.permissionNo,
        CREATED_BY=Global.operator,
        CREATED_TIME=datetime.now(),
        UPDATED_BY=Global.operator,
        UPDATED_TIME=datetime.now()
    )
    return None


@http_service
def delete_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query.filter_by(
        ROLE_NO=req.attr.roleNo,
        PERMISSION_NO=req.attr.permissionNo
    ).first()
    Verify.not_empty(role_permission, '角色权限关联关系不存在')

    role_permission.delete()
    return None
