#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from server.common.decorators.service import http_service
from server.common.id_generator import new_id
from server.common.request import RequestDTO
from server.common.validator import assert_blank, assert_not_blank
from server.user.models import TUserRoleRel, TRole, TRolePermissionRel
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_role_list(req: RequestDTO):
    # 查询条件
    conditions = [TRole.DEL_STATE == 0]

    if req.attr.roleNo:
        conditions.append(TRole.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    if req.attr.roleDesc:
        conditions.append(TRole.ROLE_DESC.like(f'%{req.attr.roleDesc}%'))
    if req.attr.state:
        conditions.append(TRole.STATE.like(f'%{req.attr.state}%'))

    pagination = TRole.query.filter(
        *conditions).order_by(TRole.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'roleNo': item.ROLE_NO,
            'roleName': item.ROLE_NAME,
            'roleDesc': item.ROLE_DESC,
            'state': item.STATE
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_role_all():
    roles = TRole.query_by().order_by(TRole.CREATED_TIME.desc()).all()
    result = []
    for role in roles:
        result.append({
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleDesc': role.ROLE_DESC,
            'state': role.STATE
        })
    return result


@http_service
def create_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NAME=req.attr.roleName).first()
    assert_blank(role, '角色已存在')

    TRole.create(
        ROLE_NO=new_id(),
        ROLE_NAME=req.attr.roleName,
        ROLE_DESC=req.attr.roleDesc,
        STATE='ENABLE'
    )
    return None


@http_service
def modify_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.attr.roleNo).first()
    assert_not_blank(role, '角色不存在')

    if req.attr.roleName is not None:
        role.ROLE_NAME = req.attr.roleName
    if req.attr.roleDesc is not None:
        role.ROLE_DESC = req.attr.roleDesc

    role.save()
    return None


@http_service
def modify_role_state(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.attr.roleNo).first()
    assert_not_blank(role, '角色不存在')

    role.update(STATE=req.attr.state)
    return None


@http_service
def delete_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.attr.roleNo).first()
    assert_not_blank(role, '角色不存在')

    user_roles = TUserRoleRel.query_by(ROLE_NO=req.attr.roleNo).all()
    assert_blank(user_roles, '角色与用户存在关联关系，请先解除关联')

    # 删除角色权限关联关系
    role_permissions = TRolePermissionRel.query_by(ROLE_NO=req.attr.roleNo).all()
    for role_permission in role_permissions:
        role_permission.update(DEL_STATE=1)

    # 删除角色
    role.update(DEL_STATE=1)
    return None
