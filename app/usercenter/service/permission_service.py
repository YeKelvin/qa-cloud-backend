#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.identity import new_id
from app.common.logger import get_logger
from app.common.validator import check_exists
from app.common.validator import check_not_exists
from app.usercenter.dao import permission_dao as PermissionDao
from app.usercenter.dao import role_permission_dao as RolePermissionDao
from app.usercenter.enum import PermissionState
from app.usercenter.model import TPermission


log = get_logger(__name__)


@http_service
def query_permission_list(req):
    # 查询权限列表
    pagination = PermissionDao.select_list(
        permissionNo=req.permissionNo,
        permissionName=req.permissionName,
        permissionDesc=req.permissionDesc,
        endpoint=req.endpoint,
        method=req.method,
        state=req.state,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for permission in pagination.items:
        data.append({
            'permissionNo': permission.PERMISSION_NO,
            'permissionName': permission.PERMISSION_NAME,
            'permissionDesc': permission.PERMISSION_DESC,
            'endpoint': permission.ENDPOINT,
            'method': permission.METHOD,
            'state': permission.STATE
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_permission_all():
    # 查询所有权限
    permissions = PermissionDao.select_all()
    result = []
    for permission in permissions:
        result.append({
            'permissionNo': permission.PERMISSION_NO,
            'permissionName': permission.PERMISSION_NAME,
            'permissionDesc': permission.PERMISSION_DESC,
            'endpoint': permission.ENDPOINT,
            'method': permission.METHOD,
            'state': permission.STATE
        })
    return result


@http_service
@transactional
def create_permission(req):
    # 查询权限
    permission = PermissionDao.select_by_endpoint_and_method(req.endpoint, req.method)
    check_not_exists(permission, '权限已存在')

    # 新增权限
    permission_no = new_id()
    TPermission.insert(
        PERMISSION_NO=permission_no,
        PERMISSION_NAME=req.permissionName,
        PERMISSION_DESC=req.permissionDesc,
        ENDPOINT=req.endpoint,
        METHOD=req.method,
        STATE=PermissionState.ENABLE.value
    )

    return {'permissionNo': permission_no}


@http_service
@transactional
def modify_permission(req):
    # 查询权限
    permission = PermissionDao.select_by_no(req.permissionNo)
    check_exists(permission, '权限不存在')

    # 唯一性校验
    if permission.PERMISSION_NAME != req.permissionName and PermissionDao.select_by_name(req.permissionName):
        raise ServiceError('分组名称已存在')

    # 更新权限信息
    permission.update(
        PERMISSION_NAME=req.permissionName,
        PERMISSION_DESC=req.permissionDesc,
        ENDPOINT=req.endpoint,
        METHOD=req.method
    )


@http_service
@transactional
def modify_permission_state(req):
    # 查询权限
    permission = PermissionDao.select_by_no(req.permissionNo)
    check_exists(permission, '权限不存在')

    # 更新权限状态
    permission.update(STATE=req.state)


@http_service
@transactional
def remove_permission(req):
    # 查询权限
    permission = PermissionDao.select_by_no(req.permissionNo)
    check_exists(permission, '权限不存在')

    # 删除角色权限
    RolePermissionDao.delete_all_by_permission(req.permissionNo)

    # 删除权限
    permission.delete()
