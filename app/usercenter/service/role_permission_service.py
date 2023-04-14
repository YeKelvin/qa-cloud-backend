#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_service.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.validator import check_exists
from app.usercenter.dao import role_dao as RoleDao
from app.usercenter.dao import role_permission_dao as RolePermissionDao
from app.usercenter.model import TPermission
from app.usercenter.model import TPermissionModule
from app.usercenter.model import TPermissionObject
from app.usercenter.model import TRolePermission
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_role_permissions(req):
    conds = QueryCondition(TPermissionModule, TPermissionObject, TPermission, TRolePermission)
    conds.equal(TRolePermission.ROLE_NO, req.roleNo)
    conds.equal(TRolePermission.PERMISSION_NO, TPermission.PERMISSION_NO)
    conds.equal(TPermission.MODULE_NO, TPermissionModule.MODULE_NO)
    conds.equal(TPermission.OBJECT_NO, TPermissionObject.OBJECT_NO)

    resutls = (
        dbquery(
            TPermissionModule.MODULE_CODE,
            TPermissionObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME
        )
        .filter(*conds)
        .order_by(TPermissionModule.MODULE_CODE.asc(), TPermissionObject.OBJECT_CODE.asc())
        .all()
    )

    return [
        {
            'permissionNo': resutl.PERMISSION_NO,
            'permissionName': resutl.PERMISSION_NAME
        }
        for resutl in resutls
    ]


@http_service
@transactional
def set_role_permissions(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, error_msg='角色不存在')

    for permission_no in req.permissionNumbers:
        # 查询角色权限
        role_permission = RolePermissionDao.select_by_role_and_permission(req.roleNo, permission_no)
        # 新增角色权限
        if not role_permission:
            TRolePermission.insert(ROLE_NO=req.roleNo, PERMISSION_NO=permission_no)

    # 删除不在请求中的角色权限
    RolePermissionDao.delete_all_by_role_and_notin_permission(req.roleNo, req.permissionNumbers)
