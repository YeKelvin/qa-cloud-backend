#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables_controller.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.enum import VariableSetType
from app.script.service import variables_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/variable/set/list')
@require_login
@require_permission
def query_variable_set_list():
    """分页查询变量集列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('setNo'),
        Argument('setName'),
        Argument('setType'),
        Argument('setDesc'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_variables_set_list(req)


@blueprint.get('/variable/set/all')
@require_login
@require_permission
def query_variable_set_all():
    """查询所有变量集"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('setNo'),
        Argument('setName'),
        Argument('setType'),
        Argument('setDesc')
    ).parse()
    return service.query_variable_set_all(req)


@blueprint.get('/variable/set')
@require_login
@require_permission
def query_variable_set():
    """查询变量集下的所有变量"""
    req = JsonParser(
        Argument('setNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.query_variable_set(req)


@blueprint.post('/variable/set')
@require_login
@require_permission
def create_variable_set():
    """新增变量集"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('setName', required=True, nullable=False, help='变量集名称不能为空'),
        Argument('setType', required=True, nullable=False, enum=VariableSetType, help='变量集类型不能为空'),
        Argument('setDesc')
    ).parse()
    return service.create_variable_set(req)


@blueprint.put('/variable/set')
@require_login
@require_permission
def modify_variable_set():
    """修改变量集"""
    req = JsonParser(
        Argument('setNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('setName', required=True, nullable=False, help='变量集名称不能为空'),
        Argument('setDesc')
    ).parse()
    return service.modify_variable_set(req)


@blueprint.delete('/variable/set')
@require_login
@require_permission
def delete_variable_set():
    """删除变量集"""
    req = JsonParser(
        Argument('setNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.delete_variable_set(req)


@blueprint.post('/variable')
@require_login
@require_permission
def create_variable():
    """新增变量"""
    req = JsonParser(
        Argument('setNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('varName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('initialValue', required=True, nullable=False, help='变量值不能为空'),
        Argument('currentValue'),
        Argument('varDesc')
    ).parse()
    return service.create_variable(req)


@blueprint.put('/variable')
@require_login
@require_permission
def modify_variable():
    """修改变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空'),
        Argument('varName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('initialValue', required=True, nullable=False, help='变量值不能为空'),
        Argument('currentValue'),
        Argument('varDesc')
    ).parse()
    return service.modify_variable(req)


@blueprint.delete('/variable')
@require_login
@require_permission
def delete_variable():
    """删除变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.delete_variable(req)


@blueprint.patch('/variable/enable')
@require_login
@require_permission
def enable_variable():
    """启用变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.enable_variable(req)


@blueprint.patch('/variable/disable')
@require_login
@require_permission
def disable_variable():
    """禁用变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.disable_variable(req)


@blueprint.patch('/variable/current/value')
@require_login
@require_permission
def update_current_value():
    """更新变量当前值"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空'),
        Argument('currentValue')
    ).parse()
    return service.update_current_value(req)


@blueprint.post('/variables')
@require_login
@require_permission
def create_variables():
    """
    根据列表批量新增变量

    example:
    {
        "setNo": "",
        "varList": [
            "varName": "",
            "initialValue": "",
            "currentValue": "",
            "varDesc": ""
        ]
    }
    """
    req = JsonParser(
        Argument('setNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('varList', type=list, required=True, nullable=False, help='变量列表不能为空')
    ).parse()
    return service.create_variables(req)


@blueprint.put('/variables')
@require_login
@require_permission
def modify_variables():
    """
    根据列表批量修改变量

    example:
    {
        "varList": [
            "varNo": "",
            "varName": "",
            "initialValue": "",
            "currentValue": "",
            "varDesc": ""
        ]
    }
    """
    req = JsonParser(
        Argument('varList', type=list, required=True, nullable=False, help='变量列表不能为空')
    ).parse()
    return service.modify_variables(req)


@blueprint.delete('/variables')
@require_login
@require_permission
def delete_variables():
    """
    根据列表批量删除变量

    example:
    {
        "varNoList": [1, 2, 3]
    }
    """
    req = JsonParser(
        Argument('varNoList', type=list, required=True, nullable=False, help='变量编号列表不能为空')
    ).parse()
    return service.delete_variables(req)
