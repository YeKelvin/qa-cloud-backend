#!/usr/bin/ python3
# @File    : workspace_user_controller.py
# @Time    : 2021-09-24 22:47:22
# @Author  : Kelvin.Ye
from app.public.controller import blueprint
from app.public.service import workspace_user_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/workspace/user/list')
@require_login
@require_permission('QUERY_WORKSPACE_MEMBER')
def query_workspace_user_list():
    """分页查询空间用户列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_workspace_user_list(req)


@blueprint.get('/workspace/user/all')
@require_login
@require_permission('QUERY_WORKSPACE_MEMBER')
def query_workspace_user_all():
    """查询所有空间用户"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_user_all(req)


@blueprint.put('/workspace/user')
@require_login
@require_permission('MODIFY_WORKSPACE_MEMBER')
def modify_workspace_user():
    """修改空间用户"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('userNos')
    ).parse()
    return service.modify_workspace_user(req)
