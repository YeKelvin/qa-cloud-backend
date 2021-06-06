#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.user.dao import permission_dao as PermissionDao
from app.user.enum import PermissionState
from app.user.model import TPermission
from app.utils.log_util import get_logger


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
def create_permission(req):
    # 查询权限
    permission = PermissionDao.select_by_endpoint_and_method(req.endpoint, req.method)
    check_is_blank(permission, '权限已存在')

    TPermission.insert(
        PERMISSION_NO=new_id(),
        PERMISSION_NAME=req.permissionName,
        PERMISSION_DESC=req.permissionDesc,
        ENDPOINT=req.endpoint,
        METHOD=req.method,
        STATE=PermissionState.ENABLE.value
    )


@http_service
def modify_permission(req):
    # 查询权限
    permission = PermissionDao.select_by_permissionno(req.permissionNo)
    check_is_not_blank(permission, '权限不存在')

    # 更新权限信息
    permission.update(
        PERMISSION_NO=req.permissionNo,
        PERMISSION_NAME=req.permissionName,
        PERMISSION_DESC=req.permissionDesc,
        ENDPOINT=req.endpoint,
        METHOD=req.method
    )


@http_service
def modify_permission_state(req):
    # 查询权限
    permission = PermissionDao.select_by_permissionno(req.permissionNo)
    check_is_not_blank(permission, '权限不存在')

    # 更新权限状态
    permission.update(STATE=req.state)


@http_service
def delete_permission(req):
    # 查询权限
    permission = PermissionDao.select_by_permissionno(req.permissionNo)
    check_is_not_blank(permission, '权限不存在')

    # 删除权限
    permission.delete()
