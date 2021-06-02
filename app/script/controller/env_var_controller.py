#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : env_var_controller.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import env_var_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/environment/variable/list')
@require_login
@require_permission
def query_environment_variable_list():
    """分页查询环境变量列表
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_environment_variable_list(req)


@blueprint.get('/environment/variable/all')
@require_login
@require_permission
def query_environment_variable_all():
    """查询所有环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.query_environment_variable_all(req)


@blueprint.post('/environment/variable')
@require_login
@require_permission
def create_environment_variable():
    """新增环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.create_environment_variable(req)


@blueprint.put('/environment/variable')
@require_login
@require_permission
def modify_environment_variable():
    """修改环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.modify_environment_variable(req)


@blueprint.delete('/environment/variable')
@require_login
@require_permission
def delete_environment_variable():
    """删除环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.delete_environment_variable(req)
