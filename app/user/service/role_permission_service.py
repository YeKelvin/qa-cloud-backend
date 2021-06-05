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
    conditions = QueryCondition()
    conditions.add_fully_match(TRole.DEL_STATE, 0)
    conditions.add_fully_match(TPermission.DEL_STATE, 0)
    conditions.add_fully_match(TRolePermissionRel.DEL_STATE, 0)
    conditions.add_fully_match(TRolePermissionRel.ROLE_NO, TRole.ROLE_NO)
    conditions.add_fully_match(TRolePermissionRel.PERMISSION_NO, TPermission.PERMISSION_NO)
    conditions.add_fuzzy_match(TRolePermissionRel.ROLE_NO, req.roleNo)
    conditions.add_fuzzy_match(TRolePermissionRel.PERMISSION_NO, req.permissionNo)
    conditions.add_fuzzy_match(TRole.ROLE_NAME, req.roleName)
    conditions.add_fuzzy_match(TPermission.PERMISSION_NAME, req.permissionName)
    conditions.add_fuzzy_match(TPermission.ENDPOINT, req.endpoint)
    conditions.add_fuzzy_match(TPermission.METHOD, req.method)

    results = db.session.query(
        TRolePermissionRel.ROLE_NO, TRolePermissionRel.PERMISSION_NO, TRole.ROLE_NAME, TPermission.PERMISSION_NAME,
        TPermission.ENDPOINT, TPermission.METHOD, TRolePermissionRel.CREATED_TIME
    ).filter(*conditions).order_by(TRolePermissionRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for result in results.items:
        data.append({
            'roleNo': result.ROLE_NO,
            'roleName': result.ROLE_NAME,
            'permissionNo': result.PERMISSION_NO,
            'permissionName': result.PERMISSION_NAME,
            'endpoint': result.ENDPOINT,
            'method': result.METHOD
        })

    return {'data': data, 'total': results.total}


@http_service
def create_role_permission_rel(req):
    role_permission = RolePermissionRelDao.select_by_roleno_and_permissionno(req.roleNo, req.permissionNo).first()
    check_is_blank(role_permission, '角色权限关联关系已存在')

    TRolePermissionRel.insert(ROLE_NO=req.roleNo, PERMISSION_NO=req.permissionNo)


@http_service
def delete_role_permission_rel(req):
    role_permission = RolePermissionRelDao.select_by_roleno_and_permissionno(req.roleNo, req.permissionNo).first()
    check_is_not_blank(role_permission, '角色权限关联关系不存在')

    role_permission.delete()
