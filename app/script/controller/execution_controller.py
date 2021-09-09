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
    """
    运行脚本

    example:
    {
        "collectionNo": "",
        "variableSet": {
            "useCurrentValue": true,
            "numberList": []
        },
        "socketId": ""
    }
    """
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='集合编号不能为空'),
        Argument('variableSet', type=dict),
        Argument('socketId')
    ).parse()
    return service.execute_collection(req)


# @blueprint.post('/execute/group')
# @require_login
# @require_permission
# def execute_group():
#     req = JsonParser(
#         Argument('groupNo', required=True, nullable=False, help='集合编号不能为空')
#         Argument('variableSet', type=dict),
#         Argument('socketId')
#     ).parse()
#     return service.execute_group(req)


# @blueprint.post('/execute/sampler')
# @require_login
# @require_permission
# def execute_sampler():
#     req = JsonParser(
#         Argument('samplerNo', required=True, nullable=False, help='集合编号不能为空')
#         Argument('variableSet', type=dict),
#         Argument('socketId')
#     ).parse()
#     return service.execute_sampler(req)


@blueprint.post('/execute/testplan')
@require_login
@require_permission
def execute_testplan():
    """
    运行测试计划

    request:
    {
        "collectionList": [
            {"elementNo": "", "serialNo": ""},
            {"elementNo": "", "serialNo": ""}
            ...
        ],
        "variableSetNumberList": [],
        "workspaceNo": "",
        "versionNo": "",
        "planName": "",
        "planDesc": "",
        "iterations": "1",
        "delay": "0",
        "save": true,
        "useCurrentValue": false,
        "executeNow": true
    }
    """
    req = JsonParser(
        Argument('collectionList', type=dict, required=True, nullable=False, help='集合列表不能为空'),
        Argument('variableSetNumberList', type=list),
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('versionNo'),
        Argument('planName', required=True, nullable=False, help='计划名称不能为空'),
        Argument('planDesc'),
        Argument('iterations', default=1),
        Argument('delay', default=0),
        Argument('save', default=True),
        Argument('useCurrentValue', default=False),
        Argument('executeNow', default=True)
    ).parse()
    return service.execute_testplan(req)
