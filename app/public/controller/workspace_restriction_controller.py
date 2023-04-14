#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_restriction_controller.py
# @Time    : 2022/4/22 16:10
# @Author  : Kelvin.Ye
from app.public.controller import blueprint
from app.public.service import workspace_restriction_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/workspace/restriction')
@require_login
@require_permission('QUERY_WORKSPACE_RESTRICTION')
def query_workspace_restriction():
    """查询空间全部限制"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_restriction(req)


@blueprint.post('/workspace/restriction')
@require_login
@require_permission('SET_WORKSPACE_RESTRICTION')
def set_workspace_restriction():
    """设置空间限制"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('permissionNumbers', type=list),
        Argument('userNumbers', type=list),
        Argument('groupNumbers', type=list)
    ).parse()
    return service.set_workspace_restriction(req)
