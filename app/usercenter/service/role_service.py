#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.id_generator import new_id
from app.common.validator import check_not_exists
from app.common.validator import check_exists
from app.usercenter.dao import role_dao as RoleDao  # noqa
from app.usercenter.dao import role_permission_dao as RolePermissionDao  # noqa
from app.usercenter.dao import user_role_dao as UserRoleDao  # noqa
from app.usercenter.enum import RoleState
from app.usercenter.model import TRole
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_role_list(req):
    # 查询角色列表
    pagination = RoleDao.select_list(
        roleNo=req.roleNo,
        roleName=req.roleName,
        roleCode=req.roleCode,
        roleDesc=req.roleDesc,
        roleType=req.roleType,
        state=req.state,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for role in pagination.items:
        if role.ROLE_CODE == 'SUPER_ADMIN':
            continue
        data.append({
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleCode': role.ROLE_CODE,
            'roleDesc': role.ROLE_DESC,
            'roleType': role.ROLE_TYPE,
            'roleRank': role.ROLE_RANK,
            'state': role.STATE
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_role_all():
    # 查询所有角色
    roles = RoleDao.select_all()
    result = []
    for role in roles:
        if role.ROLE_CODE == 'SUPER_ADMIN':
            continue
        result.append({
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleCode': role.ROLE_CODE,
            'roleDesc': role.ROLE_DESC,
            'roleType': role.ROLE_TYPE,
            'roleRank': role.ROLE_RANK,
            'state': role.STATE
        })
    return result


@http_service
def query_role_info(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, '角色不存在')

    return {
        'roleNo': role.ROLE_NO,
        'roleName': role.ROLE_NAME,
        'roleCode': role.ROLE_CODE,
        'roleDesc': role.ROLE_DESC,
        'roleType': role.ROLE_TYPE,
        'roleRank': role.ROLE_RANK,
        'state': role.STATE
    }


@http_service
@transactional
def create_role(req):
    # 唯一性校验
    if RoleDao.select_by_name(req.roleName):
        raise ServiceError('角色名称已存在')
    if RoleDao.select_by_code(req.roleCode):
        raise ServiceError('角色代码已存在')

    # 创建角色
    TRole.insert(
        ROLE_NO=new_id(),
        ROLE_NAME=req.roleName,
        ROLE_CODE=req.roleCode,
        ROLE_RANK=req.roleRank,
        ROLE_DESC=req.roleDesc,
        ROLE_TYPE='CUSTOM',
        STATE=RoleState.ENABLE.value
    )


@http_service
@transactional
def modify_role(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, '角色不存在')

    # 唯一性校验
    if role.ROLE_NAME != req.roleName and RoleDao.select_by_name(req.roleName):
        raise ServiceError('角色名称已存在')
    if role.ROLE_CODE != req.roleCode and RoleDao.select_by_code(req.roleCode):
        raise ServiceError('角色代码已存在')

    # 更新角色信息
    role.update(
        ROLE_NAME=req.roleName,
        ROLE_CODE=req.roleCode,
        ROLE_RANK=req.roleRank,
        ROLE_DESC=req.roleDesc
    )


@http_service
@transactional
def modify_role_state(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, '角色不存在')

    # 更新角色状态
    role.update(STATE=req.state)


@http_service
@transactional
def remove_role(req):
    # 查询角色
    role = RoleDao.select_by_no(req.roleNo)
    check_exists(role, '角色不存在')

    # 查询用户角色列表
    user_role_list = UserRoleDao.select_all_by_roleno(req.roleNo)
    check_not_exists(user_role_list, '角色与用户存在关联，请先解除关联')

    # 解绑角色和权限
    RolePermissionDao.delete_by_roleno(req.roleNo)

    # 删除角色
    role.delete()
