#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.request import RequestDTO
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.user.model import TPermission
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_permission_list(req: RequestDTO):
    # 查询条件
    conditions = [TPermission.DEL_STATE == 0]

    if req.permissionNo:
        conditions.append(TPermission.PERMISSION_NO.like(f'%{req.permissionNo}%'))
    if req.permissionName:
        conditions.append(TPermission.PERMISSION_NAME.like(f'%{req.permissionName}%'))
    if req.permissionDesc:
        conditions.append(TPermission.PERMISSION_DESC.like(f'%{req.permissionDesc}%'))
    if req.endpoint:
        conditions.append(TPermission.ENDPOINT.like(f'%{req.endpoint}%'))
    if req.method:
        conditions.append(TPermission.METHOD.like(f'%{req.method}%'))
    if req.state:
        conditions.append(TPermission.STATE.like(f'%{req.state}%'))

    pagination = TPermission.query.filter(
        *conditions).order_by(TPermission.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

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
    permission = TPermission.query_by(ENDPOINT=req.endpoint, METHOD=req.method).first()
    check_is_blank(permission, '权限已存在')

    TPermission.create(
        PERMISSION_NO=new_id(),
        PERMISSION_NAME=req.permissionName,
        PERMISSION_DESC=req.permissionDesc,
        ENDPOINT=req.endpoint,
        METHOD=req.method,
        STATE='ENABLE'
    )
    return None


@http_service
def modify_permission(req: RequestDTO):
    permission = TPermission.query_by(PERMISSION_NO=req.permissionNo).first()
    check_is_not_blank(permission, '权限不存在')

    if req.permissionNo is not None:
        permission.PERMISSION_NO = req.permissionNo
    if req.permissionName is not None:
        permission.PERMISSION_NAME = req.permissionName
    if req.permissionDesc is not None:
        permission.PERMISSION_DESC = req.permissionDesc
    if req.endpoint is not None:
        permission.ENDPOINT = req.endpoint
    if req.method is not None:
        permission.METHOD = req.method

    permission.save()
    return None


@http_service
def modify_permission_state(req: RequestDTO):
    permission = TPermission.query_by(PERMISSION_NO=req.permissionNo).first()
    check_is_not_blank(permission, '权限不存在')

    permission.update(STATE=req.state)
    return None


@http_service
def delete_permission(req: RequestDTO):
    permission = TPermission.query_by(PERMISSION_NO=req.permissionNo).first()
    check_is_not_blank(permission, '权限不存在')

    permission.update(DEL_STATE=1)
    return None
