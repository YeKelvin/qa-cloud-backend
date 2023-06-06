#!/usr/bin/ python3
# @File    : report_controller.py
# @Time    : 2021/9/22 14:20
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.service import report_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


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
    """根据集合ID查询结果列表"""
    req = JsonParser(Argument('collectionId', required=True, nullable=False, help='collectionId不能为空')).parse()
    return service.query_collection_result(req)


@blueprint.get('/report/worker/result')
@require_login
@require_permission('QUERY_TESTREPORT')
def query_worker_result():
    """根据用例ID查询结果列表"""
    req = JsonParser(Argument('workerId', required=True, nullable=False, help='workerId不能为空')).parse()
    return service.query_worker_result(req)


@blueprint.get('/report/sampler/result')
@require_login
@require_permission('QUERY_TESTREPORT')
def query_sampler_result():
    """根据取样器ID查询结果"""
    req = JsonParser(Argument('samplerId', required=True, nullable=False, help='samplerId不能为空')).parse()
    return service.query_sampler_result(req)
