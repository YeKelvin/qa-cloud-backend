#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_controller.py
# @Time    : 2020/3/17 14:31
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import testplan_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/testplan/list')
@require_login
@require_permission
def query_testplan_list():
    """分页查询测试计划列表"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间不能为空'),
        Argument('versionNo'),
        Argument('planNo'),
        Argument('planName'),
        Argument('runningState'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_testplan_list(req)


@blueprint.get('/testplan/all')
@require_login
@require_permission
def query_testplan_all():
    """查询所有测试计划"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('versionNo'),
        Argument('planNo'),
        Argument('planName'),
        Argument('runningState')
    ).parse()
    return service.query_testplan_all(req)


@blueprint.get('/testplan/details')
@require_login
@require_permission
def query_testplan_details():
    """查询测试计划详情"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空')
    ).parse()
    return service.query_testplan_details(req)


@blueprint.get('/testplan/report')
@require_login
@require_permission
def query_testplan_report():
    """查询测试报告"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='报告编号不能为空')
    ).parse()
    return service.query_testplan_report(req)
