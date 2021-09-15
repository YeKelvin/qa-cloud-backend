#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : report_controller.py
# @Time    : 2021-09-09 21:14:00
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import report_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/testreport/list')
@require_login
@require_permission
def query_test_report_list():
    """分页查询报告列表"""
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_test_report_list(req)


@blueprint.get('/testreport/all')
@require_login
@require_permission
def query_test_report_all():
    """查询所有报告"""
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.query_test_report_all(req)


@blueprint.get('/testreport/info')
@require_login
@require_permission
def query_test_report_info():
    """查询测试计划信息"""
    req = JsonParser(
        Argument('reportNo', required=True, nullable=False, help='报告编号不能为空'),
    ).parse()
    return service.query_test_report_info(req)
