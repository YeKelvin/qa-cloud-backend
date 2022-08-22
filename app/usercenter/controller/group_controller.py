#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group_controller.py
# @Time    : 2022/4/25 10:30
# @Author  : Kelvin.Ye
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.enum import GroupState
from app.usercenter.service import group_service as service


log = get_logger(__name__)


@blueprint.get('/group/list')
@require_login
@require_permission
def query_group_list():
    """分页查询分组列表"""
    req = JsonParser(
        Argument('groupNo'),
        Argument('groupName'),
        Argument('groupDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_group_list(req)


@blueprint.get('/group/all')
@require_login
@require_permission
def query_group_all():
    """查询所有分组"""
    return service.query_group_all()


@blueprint.get('/group/info')
@require_login
@require_permission
def query_group_info():
    """查询分组信息"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空')
    ).parse()
    return service.query_group_info(req)


@blueprint.post('/group')
@require_login
@require_permission
def create_group():
    """新增分组"""
    req = JsonParser(
        Argument('groupName', required=True, nullable=False, help='分组名称不能为空'),
        Argument('groupDesc'),
        Argument('roleNos', type=list)
    ).parse()
    return service.create_group(req)


@blueprint.put('/group')
@require_login
@require_permission
def modify_group():
    """更新分组信息"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空'),
        Argument('groupName', required=True, nullable=False, help='分组名称不能为空'),
        Argument('groupDesc'),
        Argument('roleNos', type=list)
    ).parse()
    return service.modify_group(req)


@blueprint.patch('/group/state')
@require_login
@require_permission
def modify_group_state():
    """更新分组状态"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空'),
        Argument('state', required=True, nullable=False, enum=GroupState, help='分组状态不能为空')
    ).parse()
    return service.modify_group_state(req)


@blueprint.delete('/group')
@require_login
@require_permission
def remove_group():
    """删除分组"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空')
    ).parse()
    return service.remove_group(req)
