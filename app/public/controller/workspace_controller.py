#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_controller.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from app.public.controller import blueprint
from app.public.service import workspace_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser


log = get_logger(__name__)


@blueprint.get('/workspace/list')
@require_login
@require_permission
def query_workspace_list():
    """分页查询工作空间列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('workspaceScope'),
        Argument('workspaceDesc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_workspace_list(req)


@blueprint.get('/workspace/all')
@require_login
@require_permission
def query_workspace_all():
    """查询全部工作空间"""
    req = JsonParser(
        Argument('userNo')
    ).parse()
    return service.query_workspace_all(req)


@blueprint.get('/workspace/info')
@require_login
@require_permission
def query_workspace_info():
    """查询工作空间信息"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空')
    ).parse()
    return service.query_workspace_info(req)


@blueprint.post('/workspace')
@require_login
@require_permission
def create_workspace():
    """新增工作空间"""
    req = JsonParser(
        Argument('workspaceName', required=True, nullable=False, help='工作空间名称不能为空'),
        Argument('workspaceScope', required=True, nullable=False, help='工作空间作用域不能为空'),
        Argument('workspaceDesc'),
    ).parse()
    return service.create_workspace(req)


@blueprint.put('/workspace')
@require_login
@require_permission
def modify_workspace():
    """修改工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
        Argument('workspaceName', required=True, nullable=False, help='工作空间名称不能为空'),
        Argument('workspaceScope', required=True, nullable=False, help='工作空间作用域不能为空'),
        Argument('workspaceDesc'),
    ).parse()
    return service.modify_workspace(req)


@blueprint.delete('/workspace')
@require_login
@require_permission
def remove_workspace():
    """删除工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
    ).parse()
    return service.remove_workspace(req)
