#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from server.common.id_generator import new_id
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.verification import Verify
from server.user.models import TPermission
from server.common.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_permission_list(req: RequestDTO):
    # 查询条件
    conditions = [TPermission.DEL_STATE == 0]

    if req.attr.permissionNo:
        conditions.append(TPermission.PERMISSION_NO.like(f'%{req.attr.permissionNo}%'))
    if req.attr.permissionName:
        conditions.append(TPermission.PERMISSION_NAME.like(f'%{req.attr.permissionName}%'))
    if req.attr.permissionDesc:
        conditions.append(TPermission.PERMISSION_DESC.like(f'%{req.attr.permissionDesc}%'))
    if req.attr.endpoint:
        conditions.append(TPermission.ENDPOINT.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        conditions.append(TPermission.METHOD.like(f'%{req.attr.method}%'))
    if req.attr.state:
        conditions.append(TPermission.STATE.like(f'%{req.attr.state}%'))

    pagination = TPermission.query.filter(
        *conditions).order_by(TPermission.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'permissionNo': item.PERMISSION_NO,
            'permissionName': item.PERMISSION_NAME,
            'permissionDesc': item.PERMISSION_DESC,
            'endpoint': item.ENDPOINT,
            'method': item.METHOD,
            'state': item.STATE
        })

    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_permission_all():
    permissions = TPermission.query_by().order_by(TPermission.CREATED_TIME.desc()).all()
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
def create_permission(req: RequestDTO):
    permission = TPermission.query_by(ENDPOINT=req.attr.endpoint, METHOD=req.attr.method).first()
    Verify.empty(permission, '权限已存在')

    TPermission.create(
        PERMISSION_NO=new_id(),
        PERMISSION_NAME=req.attr.permissionName,
        PERMISSION_DESC=req.attr.permissionDesc,
        ENDPOINT=req.attr.endpoint,
        METHOD=req.attr.method,
        STATE='ENABLE'
    )
    return None


@http_service
def modify_permission(req: RequestDTO):
    permission = TPermission.query_by(PERMISSION_NO=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    if req.attr.permissionNo is not None:
        permission.PERMISSION_NO = req.attr.permissionNo
    if req.attr.permissionName is not None:
        permission.PERMISSION_NAME = req.attr.permissionName
    if req.attr.permissionDesc is not None:
        permission.PERMISSION_DESC = req.attr.permissionDesc
    if req.attr.endpoint is not None:
        permission.ENDPOINT = req.attr.endpoint
    if req.attr.method is not None:
        permission.METHOD = req.attr.method

    permission.save()
    return None


@http_service
def modify_permission_state(req: RequestDTO):
    permission = TPermission.query_by(PERMISSION_NO=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    permission.update(STATE=req.attr.state)
    return None


@http_service
def delete_permission(req: RequestDTO):
    permission = TPermission.query_by(PERMISSION_NO=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    permission.update(DEL_STATE=1)
    return None
