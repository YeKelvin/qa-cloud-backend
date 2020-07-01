#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from server.common.number_generator import generate_no
from server.extensions import db
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.user.model import TUser, TUserRoleRel, TRole, TPermission, TRolePermissionRel
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_role_list(req: RequestDTO):
    # 查询条件
    conditions = [TRole.DEL_STATE == 0]

    if req.attr.roleNo:
        conditions.append(TRole.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    if req.attr.roleDesc:
        conditions.append(TRole.ROLE_DESC.like(f'%{req.attr.roleDesc}%'))
    if req.attr.state:
        conditions.append(TRole.STATE.like(f'%{req.attr.state}%'))

    pagination = TRole.query.filter(
        *conditions).order_by(TRole.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'roleNo': item.ROLE_NO,
            'roleName': item.ROLE_NAME,
            'roleDesc': item.ROLE_DESC,
            'state': item.STATE
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_role_all():
    roles = TRole.query_by().order_by(TRole.CREATED_TIME.desc()).all()
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
    role = TRole.query_by(ROLE_NAME=req.attr.roleName).first()
    Verify.empty(role, '角色已存在')

    TRole.create(
        ROLE_NO=generate_no(),
        ROLE_NAME=req.attr.roleName,
        ROLE_DESC=req.attr.roleDesc,
        STATE='ENABLE'
    )
    return None


@http_service
def modify_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    if req.attr.roleName is not None:
        role.ROLE_NAME = req.attr.roleName
    if req.attr.roleDesc is not None:
        role.ROLE_DESC = req.attr.roleDesc

    role.save()
    return None


@http_service
def modify_role_state(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    role.update(STATE=req.attr.state)
    return None


@http_service
def delete_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(role, '角色不存在')

    user_roles = TUserRoleRel.query_by(ROLE_NO=req.attr.roleNo).all()
    Verify.empty(user_roles, '角色与用户存在关联关系，请先解除关联')

    # 删除角色权限关联关系
    role_permissions = TRolePermissionRel.query_by(ROLE_NO=req.attr.roleNo).all()
    for role_permission in role_permissions:
        role_permission.update(DEL_STATE=1)

    # 删除角色
    role.update(DEL_STATE=1)
    return None


@http_service
def query_user_role_rel_list(req: RequestDTO):
    # 查询条件
    conditions = [
        TUser.DEL_STATE == 0,
        TRole.DEL_STATE == 0,
        TUserRoleRel.DEL_STATE == 0,
        TUser.USER_NO == TUserRoleRel.USER_NO,
        TRole.ROLE_NO == TUserRoleRel.ROLE_NO
    ]

    if req.attr.userNo:
        conditions.append(TUserRoleRel.USER_NO.like(f'%{req.attr.userNo}%'))
    if req.attr.roleNo:
        conditions.append(TUserRoleRel.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    if req.attr.userName:
        conditions.append(TUser.USER_NAME.like(f'%{req.attr.userName}%'))

    pagination = db.session.query(
        TUserRoleRel.USER_NO,
        TUserRoleRel.ROLE_NO,
        TRole.ROLE_NAME,
        TUser.USER_NAME,
        TUserRoleRel.CREATED_TIME
    ).filter(*conditions).order_by(TUserRoleRel.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'userNo': item.USER_NO,
            'roleNo': item.ROLE_NO,
            'userName': item.USER_NAME,
            'roleName': item.ROLE_NAME,
        })

    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def create_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query_by(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo).first()
    Verify.empty(user_role, '用户角色关联关系已存在')

    TUserRoleRel.create(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo)
    return None


@http_service
def delete_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query_by(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(user_role, '用户角色关联关系不存在')

    user_role.update(DEL_STATE=1)
    return None


@http_service
def query_role_permission_rel_list(req: RequestDTO):
    # 查询条件
    conditions = [
        TRole.DEL_STATE == 0,
        TPermission.DEL_STATE == 0,
        TRolePermissionRel.DEL_STATE == 0,
        TRole.ROLE_NO == TRolePermissionRel.ROLE_NO,
        TPermission.PERMISSION_NO == TRolePermissionRel.PERMISSION_NO
    ]

    if req.attr.roleNo:
        conditions.append(TRolePermissionRel.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.permissionNo:
        conditions.append(TRolePermissionRel.PERMISSION_NO.like(f'%{req.attr.permissionNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    if req.attr.permissionName:
        conditions.append(TPermission.PERMISSION_NAME.like(f'%{req.attr.permissionName}%'))
    if req.attr.endpoint:
        conditions.append(TPermission.ENDPOINT.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        conditions.append(TPermission.METHOD.like(f'%{req.attr.method}%'))

    pagination = db.session.query(
        TRolePermissionRel.ROLE_NO,
        TRolePermissionRel.PERMISSION_NO,
        TRole.ROLE_NAME,
        TPermission.PERMISSION_NAME,
        TPermission.ENDPOINT,
        TPermission.METHOD,
        TRolePermissionRel.CREATED_TIME
    ).filter(*conditions).order_by(TRolePermissionRel.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'roleNo': item.ROLE_NO,
            'roleName': item.ROLE_NAME,
            'permissionNo': item.PERMISSION_NO,
            'permissionName': item.PERMISSION_NAME,
            'endpoint': item.ENDPOINT,
            'method': item.METHOD
        })

    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def create_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query_by(ROLE_NO=req.attr.roleNo, PERMISSION_NO=req.attr.permissionNo).first()
    Verify.empty(role_permission, '角色权限关联关系已存在')

    TRolePermissionRel.create(ROLE_NO=req.attr.roleNo, PERMISSION_NO=req.attr.permissionNo)
    return None


@http_service
def delete_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query_by(ROLE_NO=req.attr.roleNo, PERMISSION_NO=req.attr.permissionNo).first()
    Verify.not_empty(role_permission, '角色权限关联关系不存在')

    role_permission.update(DEL_STATE=1)
    return None
