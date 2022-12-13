#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : report_controller.py
# @Time    : 2021/9/22 14:20
# @Author  : Kelvin.Ye
from app.script.controller import blueprint
from app.script.service import report_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser


log = get_logger(__name__)


@blueprint.get('/report')
@require_login
@require_permission('QUERY_TESTREPORT')
def query_report():
    """查询测试报告"""
    req = JsonParser(Argument('reportNo', required=True, nullable=False, help='报告编号不能为空')).parse()
    return service.query_report(req)


@blueprint.get('/report/collection/result')
@require_login
@require_permission('QUERY_TESTREPORT')
def query_collection_result():
    """根据集合编号查询集合结果列表和案例结果列表"""
    req = JsonParser(Argument('collectionId', required=True, nullable=False, help='collectionId不能为空')).parse()
    return service.query_collection_result(req)


@blueprint.get('/report/group/result')
@require_login
@require_permission('QUERY_TESTREPORT')
def query_group_result():
    """根据案例编号查询案例结果列表"""
    req = JsonParser(Argument('groupId', required=True, nullable=False, help='groupId不能为空')).parse()
    return service.query_group_result(req)


@blueprint.get('/report/sampler/result')
@require_login
@require_permission('QUERY_TESTREPORT')
def query_sampler_result():
    """根据取样器编号查询取样结果"""
    req = JsonParser(Argument('samplerId', required=True, nullable=False, help='samplerId不能为空')).parse()
    return service.query_sampler_result(req)
