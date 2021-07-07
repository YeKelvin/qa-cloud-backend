#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_service.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.user.dao import role_permission_rel_dao as RolePermissionRelDao
from app.user.model import TPermission
from app.user.model import TRole
from app.user.model import TRolePermissionRel
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_role_permission_rel_list(req):
    # 查询条件
    conds = QueryCondition(TRole, TPermission, TRolePermissionRel)
    conds.add_fuzzy_match(TRole.ROLE_NAME, req.roleName)
    conds.add_fuzzy_match(TPermission.PERMISSION_NAME, req.permissionName)
    conds.add_fuzzy_match(TPermission.ENDPOINT, req.endpoint)
    conds.add_fuzzy_match(TPermission.METHOD, req.method)
    conds.add_exact_match(TRolePermissionRel.ROLE_NO, TRole.ROLE_NO)
    conds.add_exact_match(TRolePermissionRel.PERMISSION_NO, TPermission.PERMISSION_NO)
    conds.add_fuzzy_match(TRolePermissionRel.ROLE_NO, req.roleNo)
    conds.add_fuzzy_match(TRolePermissionRel.PERMISSION_NO, req.permissionNo)

    # TRole，TPermission，TRolePermissionRel连表查询
    pagination = db.session.query(
        TRole.ROLE_NAME,
        TPermission.PERMISSION_NAME,
        TPermission.ENDPOINT,
        TPermission.METHOD,
        TRolePermissionRel.ROLE_NO,
        TRolePermissionRel.PERMISSION_NO,
        TRolePermissionRel.CREATED_TIME
    ).filter(*conds).order_by(TRolePermissionRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'roleNo': item.ROLE_NO,
            'roleName': item.ROLE_NAME,
            'permissionNo': item.PERMISSION_NO,
            'permissionName': item.PERMISSION_NAME,
            'endpoint': item.ENDPOINT,
            'method': item.METHOD
        })

    return {'data': data, 'total': pagination.total}


@http_service
def create_role_permission_rel(req):
    # 查询角色权限
    role_permission = RolePermissionRelDao.select_by_roleno_and_permissionno(req.roleNo, req.permissionNo).first()
    check_is_blank(role_permission, '角色权限关联关系已存在')

    # 绑定角色和权限
    TRolePermissionRel.insert(ROLE_NO=req.roleNo, PERMISSION_NO=req.permissionNo)


@http_service
def delete_role_permission_rel(req):
    # 查询角色权限
    role_permission = RolePermissionRelDao.select_by_roleno_and_permissionno(req.roleNo, req.permissionNo).first()
    check_is_not_blank(role_permission, '角色权限关联关系不存在')

    # 解绑角色和权限
    role_permission.delete()
