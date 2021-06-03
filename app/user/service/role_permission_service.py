#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_service.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.user.model import TPermission
from app.user.model import TRole
from app.user.model import TRolePermissionRel
from app.utils.log_util import get_logger


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

    if req.roleNo:
        conditions.append(TRolePermissionRel.ROLE_NO.like(f'%{req.roleNo}%'))
    if req.permissionNo:
        conditions.append(TRolePermissionRel.PERMISSION_NO.like(f'%{req.permissionNo}%'))
    if req.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.roleName}%'))
    if req.permissionName:
        conditions.append(TPermission.PERMISSION_NAME.like(f'%{req.permissionName}%'))
    if req.endpoint:
        conditions.append(TPermission.ENDPOINT.like(f'%{req.endpoint}%'))
    if req.method:
        conditions.append(TPermission.METHOD.like(f'%{req.method}%'))

    pagination = db.session.query(
        TRolePermissionRel.ROLE_NO,
        TRolePermissionRel.PERMISSION_NO,
        TRole.ROLE_NAME,
        TPermission.PERMISSION_NAME,
        TPermission.ENDPOINT,
        TPermission.METHOD,
        TRolePermissionRel.CREATED_TIME
    ).filter(*conditions).order_by(TRolePermissionRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

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
    role_permission = TRolePermissionRel.query_by(ROLE_NO=req.roleNo, PERMISSION_NO=req.permissionNo).first()
    check_is_blank(role_permission, '角色权限关联关系已存在')

    TRolePermissionRel.create(ROLE_NO=req.roleNo, PERMISSION_NO=req.permissionNo)
    return None


@http_service
def delete_role_permission_rel(req: RequestDTO):
    role_permission = TRolePermissionRel.query_by(ROLE_NO=req.roleNo, PERMISSION_NO=req.permissionNo).first()
    check_is_not_blank(role_permission, '角色权限关联关系不存在')

    role_permission.update(DEL_STATE=1)
    return None
