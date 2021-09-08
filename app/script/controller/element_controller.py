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
    """分页查询元素列表"""
    req = JsonParser(
        Argument('elementNo'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('elementType'),
        Argument('elementClass'),
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
    """查询所有元素"""
    req = JsonParser(
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled'),
        Argument('workspaceNo'),
    ).parse()
    return service.query_element_all(req)


@blueprint.get('/element/info')
@require_login
@require_permission
def query_element_info():
    """查询元素信息"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_info(req)


@blueprint.get('/element/children')
@require_login
@require_permission
def query_element_children():
    """查询元素子代"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_element_children(req)


@blueprint.get('/elements/children')
@require_login
@require_permission
def query_elements_children():
    """根据元素编号列表查询元素子代"""
    req = JsonParser(
        Argument('elementNoList', type=list, required=True, nullable=False, help='元素编号列表不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_elements_children(req)


@blueprint.post('/element')
@require_login
@require_permission
def create_element():
    """新增元素"""
    req = JsonParser(
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('children', type=list),
        Argument('workspaceNo'),
    ).parse()
    return service.create_element(req)


@blueprint.put('/element')
@require_login
@require_permission
def modify_element():
    """修改元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('enabled'),
        Argument('property'),
        Argument('children', type=list),
    ).parse()
    return service.modify_element(req)


@blueprint.delete('/element')
@require_login
@require_permission
def remove_element():
    """删除元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.remove_element(req)


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
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
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
def create_element_children():
    """
    根据父元素编号新增子代元素（同时支持新增子代内置元素）
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "children": [
            {
                "elementName": "",
                "elementRemark": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "children": [ ... ],
                "builtIn": [ ... ]
            }
            ...
        ],
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.create_element_children(req)


@blueprint.put('/element/children')
@require_login
@require_permission
def modify_element_children():
    """
    根据父元素编号修改元素子代
    request:
    {
        "children": [
            {
                "elementName": "",
                "elementRemark": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "children": [ ... ]
            }
            ...
        ],
    }"""
    req = JsonParser(
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.modify_element_children(req)


@blueprint.patch('/element/child/move/up')
@require_login
@require_permission
def move_up_element_child():
    """上移元素"""
    req = JsonParser(
        Argument('childNo', required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.move_up_element_child(req)


@blueprint.patch('/element/child/move/down')
@require_login
@require_permission
def move_down_element_child():
    """下移元素"""
    req = JsonParser(
        Argument('childNo', required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.move_down_element_child(req)


@blueprint.post('/element/child/move')
@require_login
@require_permission
def move_element_child():
    """移动元素"""
    req = JsonParser(
        Argument('sourceChildNo', required=True, nullable=False, help='来源子元素编号不能为空'),
        # Argument('targetRootNo', required=True, nullable=False, help='目标根元素编号不能为空'),
        Argument('targetParentNo', required=True, nullable=False, help='目标父元素编号不能为空'),
        Argument('targetSerialNo', required=True, nullable=False, help='子元素序号不能为空')
    ).parse()
    return service.move_element_child(req)


@blueprint.post('/element/duplicate')
@require_login
@require_permission
def duplicate_element():
    """复制元素及其子代"""
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


@blueprint.get('/element/builtin/children')
@require_login
@require_permission
def query_element_builtin_children():
    """查询内置元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.query_element_builtin_children(req)


@blueprint.post('/element/builtin/children')
@require_login
@require_permission
def create_element_builtin_children():
    """新增内置元素"""
    req = JsonParser(
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空'),
        Argument('rootNo', required=True, nullable=True)
    ).parse()
    return service.create_element_builtin_children(req)


@blueprint.put('/element/builtin/children')
@require_login
@require_permission
def modify_element_builtin_children():
    """修改内置元素"""
    req = JsonParser(
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.modify_element_builtin_children(req)
