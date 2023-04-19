#!/usr/bin/ python3
# @File    : role_controller.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.usercenter.controller import blueprint
from app.usercenter.enum import RoleState
from app.usercenter.service import role_service as service


@blueprint.get('/role/list')
@require_login
@require_permission('QUERY_ROLE')
def query_role_list():
    """分页查询角色列表"""
    req = JsonParser(
        Argument('roleNo'),
        Argument('roleName'),
        Argument('roleCode'),
        Argument('roleDesc'),
        Argument('roleType'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_role_list(req)


@blueprint.get('/role/all')
@require_login
@require_permission('QUERY_ROLE')
def query_role_all():
    """查询全部角色"""
    return service.query_role_all()


@blueprint.get('/role/info')
@require_login
@require_permission('QUERY_ROLE')
def query_role_info():
    """查询角色信息"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.query_role_info(req)


@blueprint.post('/role')
@require_login
@require_permission('CREATE_ROLE')
def create_role():
    """新增角色"""
    req = JsonParser(
        Argument('roleName', required=True, nullable=False, help='角色名称不能为空'),
        Argument('roleCode', required=True, nullable=False, help='角色代码不能为空'),
        Argument('roleRank', type=int, max=9000, min=1, required=True, nullable=False, help='角色等级不能为空'),
        Argument('roleDesc')
    ).parse()
    return service.create_role(req)


@blueprint.put('/role')
@require_login
@require_permission('MODIFY_ROLE')
def modify_role():
    """更新角色信息"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('roleName', required=True, nullable=False, help='角色名称不能为空'),
        Argument('roleCode', required=True, nullable=False, help='角色代码不能为空'),
        Argument('roleRank', type=int, max=9000, min=1, required=True, nullable=False, help='角色等级不能为空'),
        Argument('roleDesc')
    ).parse()
    return service.modify_role(req)


@blueprint.patch('/role/state')
@require_login
@require_permission('MODIFY_ROLE')
def modify_role_state():
    """更新角色状态"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('state', required=True, nullable=False, enum=RoleState, help='角色状态不能为空')
    ).parse()
    return service.modify_role_state(req)


@blueprint.delete('/role')
@require_login
@require_permission('REMOVE_ROLE')
def remove_role():
    """删除角色"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.remove_role(req)
