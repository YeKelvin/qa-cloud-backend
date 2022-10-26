#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group_service.py
# @Time    : 2022/4/25 9:37
# @Author  : Kelvin.Ye
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.usercenter.dao import group_dao as GroupDao
from app.usercenter.dao import group_role_dao as GroupRoleDao
from app.usercenter.dao import role_dao as RoleDao
from app.usercenter.dao import user_group_dao as UserGroupDao
from app.usercenter.enum import GroupState
from app.usercenter.model import TGroup
from app.usercenter.model import TGroupRole


log = get_logger(__name__)


@http_service
def query_group_list(req):
    # 查询分组列表
    pagination = GroupDao.select_list(
        groupNo=req.groupNo,
        groupName=req.groupName,
        groupDesc=req.groupDesc,
        state=req.state,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for group in pagination.items:
        # 查询分组角色列表
        roles = []
        group_role_list = GroupRoleDao.select_all_by_group(group.GROUP_NO)
        for user_role in group_role_list:
            # 查询角色
            role = RoleDao.select_by_no(user_role.ROLE_NO)
            if not role:
                continue
            roles.append({
                'roleNo': role.ROLE_NO,
                'roleName': role.ROLE_NAME
            })
        data.append({
            'groupNo': group.GROUP_NO,
            'groupName': group.GROUP_NAME,
            'groupDesc': group.GROUP_DESC,
            'state': group.STATE,
            'roles': roles
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_group_all():
    groups = GroupDao.select_all()
    return [
        {
            'groupNo': group.GROUP_NO,
            'groupName': group.GROUP_NAME,
            'groupDesc': group.GROUP_DESC,
            'state': group.STATE
        }
        for group in groups
    ]


@http_service
def query_group_info(req):
    # 查询分组
    group = GroupDao.select_by_no(req.groupNo)
    check_exists(group, error_msg='分组不存在')

    return {
        'groupNo': group.GROUP_NO,
        'groupName': group.GROUP_NAME,
        'groupDesc': group.GROUP_DESC,
        'state': group.STATE
    }


@http_service
@transactional
def create_group(req):
    # 唯一性校验
    if GroupDao.select_by_name(req.groupName):
        raise ServiceError('分组名称已存在')

    # 创建分组
    group_no = new_id()
    TGroup.insert(
        GROUP_NO=group_no,
        GROUP_NAME=req.groupName,
        GROUP_DESC=req.groupDesc,
        STATE=GroupState.ENABLE.value
    )

    # 绑定分组角色
    if req.roleNos:
        for role_no in req.roleNos:
            TGroupRole.insert(GROUP_NO=group_no, ROLE_NO=role_no)


@http_service
@transactional
def modify_group(req):
    # 查询分组
    group = GroupDao.select_by_no(req.groupNo)
    check_exists(group, error_msg='分组不存在')

    # 唯一性校验
    if group.GROUP_NAME != req.groupName and GroupDao.select_by_name(req.groupName):
        raise ServiceError('分组名称已存在')

    # 更新分组信息
    group.update(
        GROUP_NAME=req.groupName,
        GROUP_DESC=req.groupDesc
    )

    # 绑定分组角色
    if req.roleNos:
        for role_no in req.roleNos:
            # 查询分组角色
            group_role = GroupRoleDao.select_by_group_and_role(req.groupNo, role_no)
            if group_role:
                continue
            else:
                TGroupRole.insert(GROUP_NO=req.groupNo, ROLE_NO=role_no)

        # 解绑不在请求中的角色
        GroupRoleDao.delete_all_by_group_and_notin_role(req.groupNo, req.roleNos)


@http_service
@transactional
def modify_group_state(req):
    # 查询分组
    group = GroupDao.select_by_no(req.groupNo)
    check_exists(group, error_msg='分组不存在')

    # 更新分组状态
    group.update(STATE=req.state)


@http_service
@transactional
def remove_group(req):
    # 查询分组
    group = GroupDao.select_by_no(req.groupNo)
    check_exists(group, error_msg='分组不存在')

    # 删除分组用户
    UserGroupDao.delete_all_by_group(req.groupNo)

    # 删除分组角色
    GroupRoleDao.delete_all_by_group(req.groupNo)

    # 删除分组
    group.delete()
