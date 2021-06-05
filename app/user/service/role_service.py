#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.user.dao import role_dao as RoleDao
from app.user.dao import role_permission_rel_dao as RolePermissionRelDao
from app.user.dao import user_role_rel_dao as UserRoleRelDao
from app.user.enum import RoleState
from app.user.model import TRole
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_role_list(req):
    roles = RoleDao.select_list(
        roleNo=req.roleNo,
        roleName=req.roleName,
        roleDesc=req.roleDesc,
        state=req.state,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for role in roles.items:
        data.append({
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleDesc': role.ROLE_DESC,
            'state': role.STATE
        })
    return {'data': data, 'total': roles.total}


@http_service
def query_role_all():
    roles = RoleDao.select_all()
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
def create_role(req):
    role = RoleDao.select_by_rolename(req.roleName)
    check_is_blank(role, '角色已存在')

    TRole.insert(
        ROLE_NO=new_id(),
        ROLE_NAME=req.roleName,
        ROLE_DESC=req.roleDesc,
        STATE=RoleState.ENABLE.value
    )


@http_service
def modify_role(req):
    role = RoleDao.select_by_roleno(req.roleNo)
    check_is_not_blank(role, '角色不存在')

    role.update(
        ROLE_NAME=req.roleName,
        ROLE_DESC=req.roleDesc
    )


@http_service
def modify_role_state(req):
    role = RoleDao.select_by_roleno(req.roleNo)
    check_is_not_blank(role, '角色不存在')

    role.update(STATE=req.state)


@http_service
def delete_role(req):
    role = RoleDao.select_by_roleno(req.roleNo)
    check_is_not_blank(role, '角色不存在')

    user_roles = UserRoleRelDao.select_all_by_roleno(req.roleNo)
    check_is_blank(user_roles, '角色与用户存在关联关系，请先解除关联')

    # 删除角色权限关联关系
    RolePermissionRelDao.delete_by_roleno(req.roleNo)

    # 删除角色
    role.delete()
