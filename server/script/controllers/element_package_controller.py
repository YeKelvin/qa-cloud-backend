#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_package
# @Time    : 2020/3/17 14:31
# @Author  : Kelvin.Ye
from server.common.decorators.require import require_login, require_permission
from server.common.parser import JsonParser, Argument
from server.script.controllers import blueprint
from server.script.services import element_package_service as service
from server.common.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/element/package/list', methods=['GET'])
@require_login
@require_permission
def query_element_package_list():
    """分页查询元素封装列表
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_element_package_list(req)


@blueprint.route('/element/package/all', methods=['GET'])
@require_login
@require_permission
def query_element_package_all():
    """查询所有元素封装
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.query_element_package_all(req)
