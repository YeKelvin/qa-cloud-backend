#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_restriction_controller.py
# @Time    : 2022/4/22 16:10
# @Author  : Kelvin.Ye
from app.public.controller import blueprint
from app.public.enum import RestrictionMatchMethod
from app.public.enum import RestrictionMatchType
from app.public.service import workspace_restriction_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser


log = get_logger(__name__)


@blueprint.get('/workspace/restriction/list')
@require_login
@require_permission
def query_workspace_restriction_list():
    """分页查询空间限制"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('matchMethod'),
        Argument('matchType'),
        Argument('matchContent'),
        Argument('exemptionUserName'),
        Argument('exemptionGroupName'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_workspace_restriction_list(req)


@blueprint.get('/workspace/restriction/all')
@require_login
@require_permission
def query_workspace_restriction_all():
    """查询所有空间限制"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_workspace_restriction_all(req)


@blueprint.post('/workspace/restriction')
@require_login
@require_permission
def create_workspace_restriction():
    """新增空间限制"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('matchMethod', required=True, nullable=False, enum=RestrictionMatchMethod, help='匹配方法不能为空'),
        Argument('matchType', enum=RestrictionMatchType),
        Argument('matchContent'),
        Argument('exemptionUserNos', type=list),
        Argument('exemptionGroupNos', type=list)
    ).parse()
    return service.create_workspace_restriction(req)


@blueprint.put('/workspace/restriction')
@require_login
@require_permission
def modify_workspace_restriction():
    """修改空间限制"""
    req = JsonParser(
        Argument('restrictionNo', required=True, nullable=False, help='限制编号不能为空'),
        Argument('matchMethod', required=True, nullable=False, enum=RestrictionMatchMethod, help='匹配方法不能为空'),
        Argument('matchType', enum=RestrictionMatchType),
        Argument('matchContent'),
        Argument('exemptionUserNos', type=list, default=[]),
        Argument('exemptionGroupNos', type=list, default=[])
    ).parse()
    return service.modify_workspace_restriction(req)


@blueprint.delete('/workspace/restriction')
@require_login
@require_permission
def remove_workspace_restriction():
    """删除空间限制"""
    req = JsonParser(
        Argument('restrictionNo', required=True, nullable=False, help='限制编号不能为空')
    ).parse()
    return service.remove_workspace_restriction(req)


@blueprint.patch('/workspace/restriction/enable')
@require_login
@require_permission
def enable_workspace_restriction():
    """启用空间限制"""
    req = JsonParser(
        Argument('restrictionNo', required=True, nullable=False, help='限制编号不能为空')
    ).parse()
    return service.enable_workspace_restriction(req)


@blueprint.patch('/workspace/restriction/disable')
@require_login
@require_permission
def disable_workspace_restriction():
    """禁用空间限制"""
    req = JsonParser(
        Argument('restrictionNo', required=True, nullable=False, help='限制编号不能为空')
    ).parse()
    return service.disable_workspace_restriction(req)
