#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_route
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.script.routes import blueprint
from server.script.services import element_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/element/list', methods=['GET'])
@require_login
@require_permission
def query_element_list():
    """分页查询测试元素列表
    """
    req = JsonParser(
        Argument('elementNo'),
        Argument('elementName'),
        Argument('elementComments'),
        Argument('elementType'),
        Argument('enabled'),
        Argument('property'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_element_list(req)


@blueprint.route('/element/all', methods=['GET'])
@require_login
@require_permission
def query_element_all():
    """查询所有测试元素
    """
    return service.query_element_all()


@blueprint.route('/element', methods=['POST'])
@require_login
@require_permission
def create_element():
    """新增测试元素
    """
    req = JsonParser(
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementComments'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
    ).parse()
    return service.create_element(req)


@blueprint.route('/element', methods=['PUT'])
@require_login
@require_permission
def modify_element():
    """修改测试元素
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.modify_element(req)


@blueprint.route('/element', methods=['DELETE'])
@require_login
@require_permission
def delete_element():
    """删除测试元素
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.delete_element(req)
