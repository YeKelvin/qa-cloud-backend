#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.usercenter.dao import permission_dao as PermissionDao
from app.usercenter.dao import role_permission_dao as RolePermissionDao
from app.usercenter.enum import PermissionState
from app.usercenter.model import TPermission
from app.usercenter.model import TPermissionModule
from app.usercenter.model import TPermissionObject
from app.utils.sqlalchemy_util import QueryCondition


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
    conds = QueryCondition(TPermissionModule, TPermissionObject, TPermission)
    conds.equal(TPermissionModule.MODULE_NO, TPermission.MODULE_NO)
    conds.equal(TPermissionObject.OBJECT_NO, TPermission.OBJECT_NO)
    resutls = (
        dbquery(
            TPermissionModule.MODULE_NO,
            TPermissionModule.MODULE_NAME,
            TPermissionModule.MODULE_CODE,
            TPermissionObject.OBJECT_NO,
            TPermissionObject.OBJECT_NAME,
            TPermissionObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME,
            TPermission.PERMISSION_DESC,
            TPermission.PERMISSION_CODE,
            TPermission.STATE
        )
        .filter(*conds)
        .order_by(TPermissionModule.MODULE_CODE.asc(), TPermissionObject.OBJECT_CODE.asc())
        .all()
    )
    return [
        {
            'moduleNo': resutl.MODULE_NO,
            'moduleName': resutl.MODULE_NAME,
            'moduleCode': resutl.MODULE_CODE,
            'objectNo': resutl.OBJECT_NO,
            'objectName': resutl.OBJECT_NAME,
            'objectCode': resutl.OBJECT_CODE,
            'permissionNo': resutl.PERMISSION_NO,
            'permissionName': resutl.PERMISSION_NAME,
            'permissionDesc': resutl.PERMISSION_DESC,
            'permissionCode': resutl.PERMISSION_CODE,
            'state': resutl.STATE
        }
        for resutl in resutls
    ]


# @http_service
# @transactional
# def create_permission(req):
#     # 查询权限
#     permission = PermissionDao.select_by_endpoint_and_method(req.endpoint, req.method)
#     check_not_exists(permission, error_msg='权限已存在')
#
#     # 新增权限
#     permission_no = new_id()
#     TPermission.insert(
#         PERMISSION_NO=permission_no,
#         PERMISSION_NAME=req.permissionName,
#         PERMISSION_DESC=req.permissionDesc,
#         ENDPOINT=req.endpoint,
#         METHOD=req.method,
#         STATE=PermissionState.ENABLE.value
#     )
#
#     return {'permissionNo': permission_no}


# @http_service
# @transactional
# def modify_permission(req):
#     # 查询权限
#     permission = PermissionDao.select_by_no(req.permissionNo)
#     check_exists(permission, error_msg='权限不存在')
#
#     # 唯一性校验
#     if permission.PERMISSION_NAME != req.permissionName and PermissionDao.select_by_name(req.permissionName):
#         raise ServiceError('分组名称已存在')
#
#     # 更新权限信息
#     permission.update(
#         PERMISSION_NAME=req.permissionName,
#         PERMISSION_DESC=req.permissionDesc,
#         ENDPOINT=req.endpoint,
#         METHOD=req.method
#     )


@http_service
@transactional
def modify_permission_state(req):
    # 查询权限
    permission = PermissionDao.select_by_no(req.permissionNo)
    check_exists(permission, error_msg='权限不存在')

    # 更新权限状态
    permission.update(STATE=req.state)


# @http_service
# @transactional
# def remove_permission(req):
#     # 查询权限
#     permission = PermissionDao.select_by_no(req.permissionNo)
#     check_exists(permission, error_msg='权限不存在')
#
#     # 删除角色权限
#     RolePermissionDao.delete_all_by_permission(req.permissionNo)
#
#     # 删除权限
#     permission.delete()
