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
        Argument('itemNo'),
        Argument('itemName'),
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
    req = JsonParser(
        Argument('elementType'),
        Argument('enabled'),
        Argument('itemNo'),
    ).parse()
    return service.query_element_all(req)


@blueprint.route('/element/info', methods=['GET'])
@require_login
@require_permission
def query_element_info():
    """查询测试元素信息
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
    ).parse()
    return service.query_element_info(req)


@blueprint.route('/element/child', methods=['GET'])
@require_login
@require_permission
def query_element_child():
    """查询测试元素子代
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementType'),
    ).parse()
    return service.query_element_child(req)


@blueprint.route('/element', methods=['POST'])
@require_login
@require_permission
def create_element():
    """新增测试元素（支持新增子代，子代还必须包含 order属性）
    """
    req = JsonParser(
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementComments'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('propertys', required=True, nullable=False, help='元素属性不能为空'),
        Argument('childList'),
        Argument('itemNo'),
    ).parse()
    return service.create_element(req)


@blueprint.route('/element', methods=['PUT'])
@require_login
@require_permission
def modify_element():
    """修改测试元素（支持修改子代，子代还必须包含 elementNo属性和 order属性）
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementComments'),
        Argument('elementType'),
        Argument('enabled'),
        Argument('propertys'),
        Argument('childList'),
    ).parse()
    return service.modify_element(req)


@blueprint.route('/element', methods=['DELETE'])
@require_login
@require_permission
def delete_element():
    """删除测试元素
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
    ).parse()
    return service.delete_element(req)


@blueprint.route('/element/enable', methods=['PATCH'])
@require_login
@require_permission
def enable_element():
    """启用元素
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
    ).parse()
    return service.enable_element(req)


@blueprint.route('/element/disable', methods=['PATCH'])
@require_login
@require_permission
def disable_element():
    """禁用元素
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
    ).parse()
    return service.disable_element(req)


@blueprint.route('/element/property', methods=['POST'])
@require_login
@require_permission
def add_element_property():
    """添加元素属性
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('propertyName', required=True, nullable=False, help='属性名称不能为空'),
        Argument('propertyValue', required=True, nullable=False, help='属性值不能为空'),
    ).parse()
    return service.add_element_property(req)


@blueprint.route('/element/property', methods=['PUT'])
@require_login
@require_permission
def modify_element_property():
    """修改元素属性
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('propertyName', required=True, nullable=False, help='属性名称不能为空'),
        Argument('propertyValue', required=True, nullable=False, help='属性值不能为空'),
    ).parse()
    return service.modify_element_property(req)


@blueprint.route('/element/property', methods=['DELETE'])
@require_login
@require_permission
def remove_element_property():
    """移除元素属性
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('propertyName', required=True, nullable=False, help='属性名称不能为空'),
    ).parse()
    return service.remove_element_property(req)


@blueprint.route('/element/child', methods=['POST'])
@require_login
@require_permission
def add_element_child():
    """根据父元素编号新增元素子代（子代还必须包含 order属性）
    """
    req = JsonParser(
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('childList', required=True, nullable=False, help='子元素列表不能为空'),
    ).parse()
    return service.add_element_child(req)


@blueprint.route('/element/child', methods=['PUT'])
@require_login
@require_permission
def modify_element_child():
    """根据父元素编号修改元素子代（子代还必须包含 elementNo属性和 order属性）
    """
    req = JsonParser(
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('childList', required=True, nullable=False, help='子元素列表不能为空'),
    ).parse()
    return service.modify_element_child(req)


@blueprint.route('/element/child/order', methods=['PATCH'])
@require_login
@require_permission
def modify_element_child_order():
    """修改元素子代序号
    """
    req = JsonParser(
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('childNo', required=True, nullable=False, help='子元素列表不能为空'),
        Argument('childOrder', required=True, nullable=False, help='子元素序号不能为空'),
    ).parse()
    return service.modify_element_child_order(req)
