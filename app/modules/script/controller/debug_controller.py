#!/usr/bin python3
# @File    : debug_controller.py
# @Time    : 2023-05-16 16:26:39
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.service import debug_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/collection/json')
@require_login
@require_permission('QUERY_SCRIPT_AS_JSON')
def query_collection_json():
    """查询测试集合的脚本(JSON)"""
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='集合编号不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.query_collection_json(req)


@blueprint.get('/worker/json')
@require_login
@require_permission('QUERY_SCRIPT_AS_JSON')
def query_worker_json():
    """查询测试用例的脚本(JSON)"""
    req = JsonParser(
        Argument('workerNo', required=True, nullable=False, help='工作者编号不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.query_worker_json(req)


@blueprint.get('/snippets/json')
@require_login
@require_permission('QUERY_SCRIPT_AS_JSON')
def query_snippets_json():
    """查询片段集合的脚本(JSON)"""
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='集合编号不能为空'),
        Argument('datasets', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.query_snippets_json(req)
