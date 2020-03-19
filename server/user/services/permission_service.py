#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from server.librarys.decorators.service import http_service
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.verify import Verify
from server.user.model import TPermission
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_permission_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.permissionNo:
        conditions.append(TPermission.permission_no == req.attr.permissionNo)
    if req.attr.permissionName:
        conditions.append(TPermission.permission_name.like(f'%{req.attr.permissionName}%'))
    if req.attr.endpoint:
        conditions.append(TPermission.endpoint.like(f'%{req.attr.endpoint}%'))
    if req.attr.method:
        conditions.append(TPermission.method.like(f'%{req.attr.method}%'))
    if req.attr.state:
        conditions.append(TPermission.state.like(f'%{req.attr.state}%'))

    # 列表总数
    total_size = TPermission.query.filter(*conditions).count()
    # 列表数据
    permissions = TPermission.query.filter(
        *conditions
    ).order_by(
        TPermission.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for permission in permissions:
        data_set.append({
            'permissionNo': permission.permission_no,
            'permissionName': permission.permission_name,
            'endpoint': permission.endpoint,
            'method': permission.method,
            'state': permission.state
        })

    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_permission_all():
    permissions = TPermission.query.order_by(TPermission.created_time.desc()).all()
    result = []
    for permission in permissions:
        result.append({
            'permissionNo': permission.permission_no,
            'permissionName': permission.permission_name,
            'endpoint': permission.endpoint,
            'method': permission.method,
            'state': permission.state
        })
    return result


@http_service
def create_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(endpoint=req.attr.endpoint, method=req.attr.method).first()
    Verify.empty(permission, '权限已存在')

    TPermission.create(
        permission_no=generate_permission_no(),
        permission_name=req.attr.permissionName,
        endpoint=req.attr.endpoint,
        method=req.attr.method,
        state='NORMAL',
        description=req.attr.description,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def modify_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    if req.attr.permissionNo is not None:
        permission.permission_no = req.attr.permissionNo
    if req.attr.permissionName is not None:
        permission.permission_name = req.attr.permissionName
    if req.attr.endpoint is not None:
        permission.endpoint = req.attr.endpoint
    if req.attr.method is not None:
        permission.method = req.attr.method
    permission.save()
    return None


@http_service
def modify_permission_state(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    permission.update(state=req.attr.state)
    return None


@http_service
def delete_permission(req: RequestDTO):
    permission = TPermission.query.filter_by(permission_no=req.attr.permissionNo).first()
    Verify.not_empty(permission, '权限不存在')

    permission.delete()
    return None


def generate_permission_no():
    """生成权限编号
    """
    seq_permission_no = Sequence('seq_permission_no')
    return 'P' + str(seq_permission_no.next_value()).zfill(10)
