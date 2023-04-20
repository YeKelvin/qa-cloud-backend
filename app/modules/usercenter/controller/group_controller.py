#!/usr/bin/ python3
# @File    : group_controller.py
# @Time    : 2022/4/25 10:30
# @Author  : Kelvin.Ye
from app.modules.usercenter.controller import blueprint
from app.modules.usercenter.enum import GroupState
from app.modules.usercenter.service import group_service as service
from app.tools.require import require_login
from app.tools.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/group/list')
@require_login
@require_permission('QUERY_GROUP')
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
@require_permission('QUERY_GROUP')
def query_group_all():
    """查询全部分组"""
    return service.query_group_all()


@blueprint.get('/group/info')
@require_login
@require_permission('QUERY_GROUP')
def query_group_info():
    """查询分组信息"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空')
    ).parse()
    return service.query_group_info(req)


@blueprint.post('/group')
@require_login
@require_permission('CREATE_GROUP')
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
@require_permission('MODIFY_GROUP')
def modify_group():
    """更新分组信息"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空'),
        Argument('groupName', required=True, nullable=False, help='分组名称不能为空'),
        Argument('groupDesc'),
        Argument('roleNos', type=list)
    ).parse()
    return service.modify_group(req)


@blueprint.put('/group/state')
@require_login
@require_permission('MODIFY_GROUP')
def modify_group_state():
    """更新分组状态"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空'),
        Argument('state', required=True, nullable=False, enum=GroupState, help='分组状态不能为空')
    ).parse()
    return service.modify_group_state(req)


@blueprint.delete('/group')
@require_login
@require_permission('REMOVE_GROUP')
def remove_group():
    """删除分组"""
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='分组编号不能为空')
    ).parse()
    return service.remove_group(req)
