#!/usr/bin/ python3
# @File    : workspace_user_controller.py
# @Time    : 2021-09-24 22:47:22
# @Author  : Kelvin.Ye
from app.modules.public.controller import blueprint
from app.modules.public.service import workspace_member_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/workspace/member/list')
@require_login
@require_permission('QUERY_WORKSPACE_MEMBER')
def query_workspace_member_list():
    """分页查询空间成员列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_workspace_member_list(req)


@blueprint.get('/workspace/member/all')
@require_login
@require_permission('QUERY_WORKSPACE_MEMBER')
def query_workspace_member_all():
    """查询所有空间成员"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_member_all(req)


@blueprint.put('/workspace/member')
@require_login
@require_permission('MODIFY_WORKSPACE_MEMBER')
def modify_workspace_member():
    """修改空间成员"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('members')
    ).parse()
    return service.modify_workspace_member(req)
