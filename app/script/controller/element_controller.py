#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_controller.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import element_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/element/list')
@require_login
@require_permission
def query_element_list():
    """分页查询测试元素列表"""
    req = JsonParser(
        Argument('elementNo'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('elementType'),
        Argument('enabled'),
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_element_list(req)


@blueprint.get('/element/all')
@require_login
@require_permission
def query_element_all():
    """查询所有测试元素"""
    req = JsonParser(
        Argument('elementType'),
        Argument('enabled'),
        Argument('workspaceNo'),
    ).parse()
    return service.query_element_all(req)


@blueprint.get('/element/info')
@require_login
@require_permission
def query_element_info():
    """查询测试元素信息"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_info(req)


@blueprint.get('/element/children')
@require_login
@require_permission
def query_element_children():
    """查询测试元素子代"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_element_children(req)


@blueprint.post('/element')
@require_login
@require_permission
def create_element():
    """新增测试元素（支持新增子代，子代必须包含order属性）"""
    req = JsonParser(
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('children'),
        Argument('workspaceNo'),
    ).parse()
    return service.create_element(req)


@blueprint.put('/element')
@require_login
@require_permission
def modify_element():
    """修改测试元素（支持修改子代，子代必须包含elementNo和order）"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('enabled'),
        Argument('property'),
        Argument('children'),
    ).parse()
    return service.modify_element(req)


@blueprint.delete('/element')
@require_login
@require_permission
def delete_element():
    """删除测试元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.delete_element(req)


@blueprint.patch('/element/enable')
@require_login
@require_permission
def enable_element():
    """启用元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.enable_element(req)


@blueprint.patch('/element/disable')
@require_login
@require_permission
def disable_element():
    """禁用元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),).parse()
    return service.disable_element(req)


@blueprint.post('/element/property')
@require_login
@require_permission
def create_element_property():
    """添加元素属性"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('propertyName', required=True, nullable=False, help='属性名称不能为空'),
        Argument('propertyValue', required=True, nullable=False, help='属性值不能为空'),
    ).parse()
    return service.create_element_property(req)


@blueprint.put('/element/property')
@require_login
@require_permission
def modify_element_property():
    """修改元素属性"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('propertyName', required=True, nullable=False, help='属性名称不能为空'),
        Argument('propertyValue', required=True, nullable=False, help='属性值不能为空'),
    ).parse()
    return service.modify_element_property(req)


@blueprint.post('/element/children')
@require_login
@require_permission
def create_element_child():
    """根据父元素编号新增元素子代"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', required=True, nullable=False, help='子元素列表不能为空'),
    ).parse()
    return service.create_element_children(req)


@blueprint.put('/element/children')
@require_login
@require_permission
def modify_element_child():
    """根据父元素编号修改元素子代（子代必须包含elementNo和order）"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', required=True, nullable=False, help='子元素列表不能为空'),
    ).parse()
    return service.modify_element_children(req)


@blueprint.patch('/element/child/order/up')
@require_login
@require_permission
def move_up_element_child_order():
    """根据父元素编号和子元素编号上移序号"""
    req = JsonParser(
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('childNo', required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.move_up_child_order(req)


@blueprint.patch('/element/child/order/down')
@require_login
@require_permission
def move_down_element_child_order():
    """根据父元素编号和子元素编号下移序号"""
    req = JsonParser(
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('childNo', required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.move_down_child_order(req)


@blueprint.post('/element/duplicate')
@require_login
@require_permission
def duplicate_element():
    """复制测试元素及其子代"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.duplicate_element(req)


@blueprint.get('/element/http/headers/template/list')
@require_login
@require_permission
def query_element_http_headers_template_list():
    """查询元素关联的HTTP请求头模板列表"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_http_headers_template_list(req)


@blueprint.post('/element/http/headers/template/list')
@require_login
@require_permission
def create_element_http_headers_template_list():
    """新增元素和HTTP请求头模板列表的关联"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('templateNoList', type=list, required=True, nullable=False, help='模板编号列表不能为空')
    ).parse()
    return service.create_element_http_headers_template_list(req)


@blueprint.put('/element/http/headers/template/list')
@require_login
@require_permission
def modify_element_http_headers_template_list():
    """修改元素关联的HTTP请求头模板关联列表"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('templateNoList', type=list, required=True, nullable=False, help='模板编号列表不能为空')
    ).parse()
    return service.modify_element_http_headers_template_list(req)
