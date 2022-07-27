#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_controller.py
# @Time    : 2021-09-24 22:47:22
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.logger import get_logger
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.public.controller import blueprint
from app.public.service import workspace_user_service as service


log = get_logger(__name__)


@blueprint.get('/workspace/user/list')
@require_login
@require_permission
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
@require_permission
def query_workspace_user_all():
    """查询所有空间用户"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_user_all(req)


@blueprint.put('/workspace/user')
@require_login
@require_permission
def modify_workspace_user():
    """修改空间用户"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('userNumberList')
    ).parse()
    return service.modify_workspace_user(req)
