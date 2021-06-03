#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.request import RequestDTO
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.user.model import TRole
from app.user.model import TRolePermissionRel
from app.user.model import TUserRoleRel
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_role_list(req: RequestDTO):
    # 查询条件
    conditions = [TRole.DEL_STATE == 0]

    if req.roleNo:
        conditions.append(TRole.ROLE_NO.like(f'%{req.roleNo}%'))
    if req.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.roleName}%'))
    if req.roleDesc:
        conditions.append(TRole.ROLE_DESC.like(f'%{req.roleDesc}%'))
    if req.state:
        conditions.append(TRole.STATE.like(f'%{req.state}%'))

    pagination = TRole.query.filter(
        *conditions).order_by(TRole.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

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
    role = TRole.query_by(ROLE_NAME=req.roleName).first()
    check_is_blank(role, '角色已存在')

    TRole.create(
        ROLE_NO=new_id(),
        ROLE_NAME=req.roleName,
        ROLE_DESC=req.roleDesc,
        STATE='ENABLE'
    )
    return None


@http_service
def modify_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.roleNo).first()
    check_is_not_blank(role, '角色不存在')

    if req.roleName is not None:
        role.ROLE_NAME = req.roleName
    if req.roleDesc is not None:
        role.ROLE_DESC = req.roleDesc

    role.save()
    return None


@http_service
def modify_role_state(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.roleNo).first()
    check_is_not_blank(role, '角色不存在')

    role.update(STATE=req.state)
    return None


@http_service
def delete_role(req: RequestDTO):
    role = TRole.query_by(ROLE_NO=req.roleNo).first()
    check_is_not_blank(role, '角色不存在')

    user_roles = TUserRoleRel.query_by(ROLE_NO=req.roleNo).all()
    check_is_blank(user_roles, '角色与用户存在关联关系，请先解除关联')

    # 删除角色权限关联关系
    role_permissions = TRolePermissionRel.query_by(ROLE_NO=req.roleNo).all()
    for role_permission in role_permissions:
        role_permission.update(DEL_STATE=1)

    # 删除角色
    role.update(DEL_STATE=1)
    return None
