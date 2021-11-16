#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_service.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_not_blank
from app.extension import db
from app.user.dao import role_dao as RoleDao  # noqa
from app.user.dao import role_permission_rel_dao as RolePermissionRelDao
from app.user.model import TPermission
from app.user.model import TRolePermissionRel
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_role_permission_rel_list(req):
    # 查询条件
    conds = QueryCondition(TPermission, TRolePermissionRel)
    conds.like(TPermission.PERMISSION_NAME, req.permissionName)
    conds.like(TPermission.ENDPOINT, req.endpoint)
    conds.like(TPermission.METHOD, req.method)
    conds.like(TRolePermissionRel.ROLE_NO, req.roleNo)
    conds.like(TRolePermissionRel.PERMISSION_NO, req.permissionNo)
    conds.equal(TRolePermissionRel.PERMISSION_NO, TPermission.PERMISSION_NO)

    # TRole，TPermission，TRolePermissionRel连表查询
    pagination = db.session.query(
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
            'permissionNo': item.PERMISSION_NO,
            'permissionName': item.PERMISSION_NAME,
            'endpoint': item.ENDPOINT,
            'method': item.METHOD
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_role_permission_unbound_list(req):
    # 查询条件
    bound_conds = QueryCondition(TPermission, TRolePermissionRel)
    bound_conds.like(TRolePermissionRel.ROLE_NO, req.roleNo)

    unbound_conds = QueryCondition(TPermission)
    unbound_conds.like(TPermission.PERMISSION_NO, req.permissionNo)
    unbound_conds.like(TPermission.PERMISSION_NAME, req.permissionName)
    unbound_conds.like(TPermission.ENDPOINT, req.endpoint)
    unbound_conds.like(TPermission.METHOD, req.method)

    # TRole，TPermission，TRolePermissionRel连表查询
    pagination = db.session.query(
        TPermission
    ).filter(
        ~db.session.query(TPermission).filter(*bound_conds).exists()
    ).filter(
        *unbound_conds
    ).order_by(TPermission.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'permissionNo': item.PERMISSION_NO,
            'permissionName': item.PERMISSION_NAME,
            'endpoint': item.ENDPOINT,
            'method': item.METHOD
        })

    return {'data': data, 'total': pagination.total}


@http_service
def create_role_permissions(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_is_not_blank(role, '角色不存在')

    for permission_no in req.permissionNumberList:
        # 查询角色权限
        role_permission = RolePermissionRelDao.select_by_role_and_permission(req.roleNo, permission_no)
        # 绑定角色权限
        if not role_permission:
            TRolePermissionRel.insert(ROLE_NO=req.roleNo, PERMISSION_NO=permission_no)


@http_service
def remove_role_permission(req):
    # 查询角色权限
    role_permission = RolePermissionRelDao.select_by_role_and_permission(req.roleNo, req.permissionNo)
    # 解绑角色权限
    if role_permission:
        role_permission.delete()


@http_service
def remove_role_permissions(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_is_not_blank(role, '角色不存在')

    for permission_no in req.permissionNumberList:
        # 查询角色权限
        role_permission = RolePermissionRelDao.select_by_role_and_permission(req.roleNo, permission_no)
        # 解绑角色权限
        if role_permission:
            role_permission.delete()
