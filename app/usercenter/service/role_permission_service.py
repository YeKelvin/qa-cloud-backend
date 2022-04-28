#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_service.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from sqlalchemy import and_
from sqlalchemy import exists

from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.validator import check_exists
from app.extension import db
from app.usercenter.dao import role_dao as RoleDao
from app.usercenter.dao import role_permission_dao as RolePermissionDao
from app.usercenter.model import TPermission
from app.usercenter.model import TRolePermission
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_role_permission_list(req):
    # 查询条件
    conds = QueryCondition(TPermission, TRolePermission)
    conds.like(TPermission.PERMISSION_NAME, req.permissionName)
    conds.like(TPermission.ENDPOINT, req.endpoint)
    conds.like(TPermission.METHOD, req.method)
    conds.like(TRolePermission.ROLE_NO, req.roleNo)
    conds.like(TRolePermission.PERMISSION_NO, req.permissionNo)
    conds.equal(TRolePermission.PERMISSION_NO, TPermission.PERMISSION_NO)

    # TRole，TPermission，TRolePermission连表查询
    pagination = db.session.query(
        TPermission.PERMISSION_NAME,
        TPermission.ENDPOINT,
        TPermission.METHOD,
        TRolePermission.ROLE_NO,
        TRolePermission.PERMISSION_NO,
        TRolePermission.CREATED_TIME
    ).filter(*conds).order_by(TRolePermission.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

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
    bound_conds = QueryCondition(TPermission, TRolePermission)
    bound_conds.equal(TRolePermission.PERMISSION_NO, TPermission.PERMISSION_NO)
    bound_conds.like(TRolePermission.ROLE_NO, req.roleNo)

    unbound_conds = QueryCondition(TPermission)
    unbound_conds.like(TPermission.PERMISSION_NO, req.permissionNo)
    unbound_conds.like(TPermission.PERMISSION_NAME, req.permissionName)
    unbound_conds.like(TPermission.ENDPOINT, req.endpoint)
    unbound_conds.like(TPermission.METHOD, req.method)

    # TPermission，TRolePermission连表查询
    pagination = db.session.query(
        TPermission
    ).filter(
        ~exists().where(and_(*bound_conds))
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
@transactional
def create_role_permissions(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, '角色不存在')

    for permission_no in req.permissionNumberList:
        # 查询角色权限
        role_permission = RolePermissionDao.select_by_role_and_permission(req.roleNo, permission_no)
        # 绑定角色权限
        if not role_permission:
            TRolePermission.insert(ROLE_NO=req.roleNo, PERMISSION_NO=permission_no)


@http_service
@transactional
def remove_role_permission(req):
    # 查询角色权限
    role_permission = RolePermissionDao.select_by_role_and_permission(req.roleNo, req.permissionNo)
    # 解绑角色权限
    if role_permission:
        role_permission.delete()


@http_service
@transactional
def remove_role_permissions(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, '角色不存在')

    for permission_no in req.permissionNumberList:
        # 查询角色权限
        role_permission = RolePermissionDao.select_by_role_and_permission(req.roleNo, permission_no)
        # 解绑角色权限
        if role_permission:
            role_permission.delete()
