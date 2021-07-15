#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : environment_controller.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import environment_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/environment/list')
@require_login
@require_permission
def query_environment_list():
    """分页查询环境变量配置列表"""
    req = JsonParser(
        Argument('envNo'),
        Argument('envName'),
        Argument('envDesc'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_environment_list(req)


@blueprint.get('/environment/all')
@require_login
@require_permission
def query_environment_all():
    """查询所有环境变量配置"""
    req = JsonParser(
        Argument('envNo'),
        Argument('envName'),
        Argument('envDesc')
    ).parse()
    return service.query_environment_all(req)


@blueprint.post('/environment')
@require_login
@require_permission
def create_environment():
    """新增环境变量配置"""
    req = JsonParser(
        Argument('envName', required=True, nullable=False, help='环境名称不能为空'),
        Argument('envDesc')
    ).parse()
    return service.create_environment(req)


@blueprint.put('/environment')
@require_login
@require_permission
def modify_environment():
    """修改环境变量配置"""
    req = JsonParser(
        Argument('envNo', required=True, nullable=False, help='环境编号不能为空'),
        Argument('envName', required=True, nullable=False, help='环境名称不能为空'),
        Argument('envDesc'),
    ).parse()
    return service.modify_environment(req)


@blueprint.delete('/environment')
@require_login
@require_permission
def delete_environment():
    """删除环境变量配置"""
    req = JsonParser(
        Argument('envNo', required=True, nullable=False, help='环境编号不能为空')
    ).parse()
    return service.delete_environment(req)


@blueprint.post('/environment/variable')
@require_login
@require_permission
def create_environment_variable():
    """新增环境变量"""
    req = JsonParser(
        Argument('envNo', required=True, nullable=False, help='环境编号不能为空'),
        Argument('varName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('varValue', required=True, nullable=False, help='变量值不能为空'),
        Argument('varDesc')
    ).parse()
    return service.create_environment_variable(req)


@blueprint.put('/environment/variable')
@require_login
@require_permission
def modify_environment_variable():
    """修改环境变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空'),
        Argument('varName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('varValue', required=True, nullable=False, help='变量值不能为空'),
        Argument('varDesc')
    ).parse()
    return service.modify_environment_variable(req)


@blueprint.delete('/environment/variable')
@require_login
@require_permission
def delete_environment_variable():
    """删除环境变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.delete_environment_variable(req)
