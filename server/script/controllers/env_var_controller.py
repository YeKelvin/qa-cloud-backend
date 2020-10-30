#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : env_var_route
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from server.common.decorators.require import require_login, require_permission
from server.common.parser import JsonParser, Argument
from server.script.controllers import blueprint
from server.script.services import env_var_service as service
from server.common.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/environment/variable/list', methods=['GET'])
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


@blueprint.route('/environment/variable/all', methods=['GET'])
@require_login
@require_permission
def query_environment_variable_all():
    """查询所有环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.query_environment_variable_all(req)


@blueprint.route('/environment/variable', methods=['POST'])
@require_login
@require_permission
def create_environment_variable():
    """新增环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.create_environment_variable(req)


@blueprint.route('/environment/variable', methods=['PUT'])
@require_login
@require_permission
def modify_environment_variable():
    """修改环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.modify_environment_variable(req)


@blueprint.route('/environment/variable', methods=['DELETE'])
@require_login
@require_permission
def delete_environment_variable():
    """删除环境变量
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.delete_environment_variable(req)
