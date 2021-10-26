#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_controller.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import execution_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.post('/execute/collection')
@require_login
@require_permission
def execute_collection():
    """运行脚本

    example:
    {
        "collectionNo": "",
        "socketId": "",
        "variableSet": {
            "useCurrentValue": true,
            "numberList": [ ... ]
        }
    }
    """
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='Collection 编号不能为空'),
        Argument('socketId', required=True, nullable=False, help='sid 不能为空'),
        Argument('variableDataSet', type=dict)
    ).parse()
    return service.execute_collection(req)


@blueprint.post('/execute/group')
@require_login
@require_permission
def execute_group():
    req = JsonParser(
        Argument('groupNo', required=True, nullable=False, help='Group 编号不能为空'),
        Argument('socketId', required=True, nullable=False, help='sid不能为空'),
        Argument('variableDataSet', type=dict),
        Argument('selfOnly', type=bool, default=False)
    ).parse()
    return service.execute_group(req)


@blueprint.post('/execute/sampler')
@require_login
@require_permission
def execute_sampler():
    req = JsonParser(
        Argument('samplerNo', required=True, nullable=False, help='Sampler 编号不能为空'),
        Argument('socketId', required=True, nullable=False, help='sid不能为空'),
        Argument('variableDataSet', type=dict),
        Argument('selfOnly', type=bool, default=False)
    ).parse()
    return service.execute_sampler(req)


@blueprint.post('/execute/testplan')
@require_login
@require_permission
def execute_testplan():
    """运行测试计划"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空')
    ).parse()
    return service.execute_testplan(req)


@blueprint.post('/execute/snippet/collection')
@require_login
@require_permission
def execute_snippet_collection():
    """运行脚本

    example:
    {
        "collectionNo": "",
        "socketId": "",
        "variableSet": {
            "useCurrentValue": true,
            "numberList": [ ... ]
        }
        "variables": { ... }
    }
    """
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='Collection 编号不能为空'),
        Argument('socketId', required=True, nullable=False, help='sid 不能为空'),
        Argument('variableDataSet', type=dict),
        Argument('variables', type=dict)
    ).parse()
    return service.execute_snippet_collection(req)
