#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_controller.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.system.controller import blueprint
from app.system.service import workspace_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/workspace/list')
@require_login
@require_permission
def query_workspace_list():
    """分页查询工作空间列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('workspaceType'),
        Argument('workspaceDesc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_workspace_list(req)


@blueprint.get('/workspace/all')
@require_login
@require_permission
def query_workspace_all():
    """查询所有工作空间"""
    return service.query_workspace_all()


@blueprint.post('/workspace')
@require_login
@require_permission
def create_workspace():
    """新增工作空间"""
    req = JsonParser(
        Argument('workspaceName', required=True, nullable=False, help='工作空间名称不能为空'),
        Argument('workspaceType', required=True, nullable=False, help='工作空间类型不能为空'),
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
        Argument('workspaceType', required=True, nullable=False, help='工作空间类型不能为空'),
        Argument('workspaceDesc'),
    ).parse()
    return service.modify_workspace(req)


@blueprint.delete('/workspace')
@require_login
@require_permission
def delete_workspace():
    """删除工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
    ).parse()
    return service.delete_workspace(req)


@blueprint.post('/workspace/user')
@require_login
@require_permission
def add_workspace_user():
    """添加工作空间成员"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.add_workspace_user(req)


@blueprint.put('/workspace/user')
@require_login
@require_permission
def modify_workspace_user():
    """修改工作空间成员"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.modify_workspace_user(req)


@blueprint.delete('/workspace/user')
@require_login
@require_permission
def remove_workspace_user():
    """移除工作空间成员"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.remove_workspace_user(req)
