#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_service
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from server.extension import db
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.verification import Verify
from server.user.models import TRole, TPermission, TRolePermissionRel
from server.common.utils.log_util import get_logger

log = get_logger(__name__)


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
