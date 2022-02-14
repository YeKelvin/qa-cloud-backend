#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : headers_controller.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.common.parser import ListParser
from app.script.controller import blueprint
from app.script.service import headers_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/http/header/template/list')
@require_login
@require_permission
def query_http_header_template_list():
    """分页查询请求头模板列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('templateNo'),
        Argument('templateName'),
        Argument('templateDesc'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_http_header_template_list(req)


@blueprint.get('/http/header/template/all')
@require_login
@require_permission
def query_http_header_template_all():
    """查询所有请求头模板"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('templateNo'),
        Argument('templateName'),
        Argument('templateDesc')
    ).parse()
    return service.query_http_header_template_all(req)


@blueprint.post('/http/header/template')
@require_login
@require_permission
def create_http_header_template():
    """新增请求头模板"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('templateName', required=True, nullable=False, help='模板名称不能为空'),
        Argument('templateDesc')
    ).parse()
    return service.create_http_header_template(req)


@blueprint.put('/http/header/template')
@require_login
@require_permission
def modify_http_header_template():
    """修改请求头模板"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空'),
        Argument('templateName', required=True, nullable=False, help='模板名称不能为空'),
        Argument('templateDesc')
    ).parse()
    return service.modify_http_header_template(req)


@blueprint.delete('/http/header/template')
@require_login
@require_permission
def remove_http_header_template():
    """删除请求头模板"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.remove_http_header_template(req)


@blueprint.post('/http/header')
@require_login
@require_permission
def create_http_header():
    """新增请求头"""
    req = JsonParser(
        Argument('headerName', required=True, nullable=False, help='请求头名称不能为空'),
        Argument('headerValue', required=True, nullable=False, help='请求头值不能为空'),
        Argument('headerDesc')
    ).parse()
    return service.create_http_header(req)


@blueprint.put('/http/header')
@require_login
@require_permission
def modify_http_header():
    """修改请求头"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空'),
        Argument('headerName', required=True, nullable=False, help='请求头名称不能为空'),
        Argument('headerValue', required=True, nullable=False, help='请求头值不能为空'),
        Argument('headerDesc')
    ).parse()
    return service.modify_http_header(req)


@blueprint.delete('/http/header')
@require_login
@require_permission
def remove_http_header():
    """删除请求头"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空')
    ).parse()
    return service.remove_http_header(req)


@blueprint.patch('/http/header/enable')
@require_login
@require_permission
def enable_http_header():
    """启用变量"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空')
    ).parse()
    return service.enable_http_header(req)


@blueprint.patch('/http/header/disable')
@require_login
@require_permission
def disable_http_header():
    """禁用变量"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空')
    ).parse()
    return service.disable_http_header(req)


@blueprint.get('/http/headers/by/template')
@require_login
@require_permission
def query_http_headers_by_template():
    """查询模板下的请求头"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.query_http_headers_by_template(req)


@blueprint.get('/http/headers')
@require_login
@require_permission
def query_http_headers():
    """根据列表查询请求头"""
    req = ListParser().parse()
    return service.query_http_headers(req)


@blueprint.post('/http/headers')
@require_login
@require_permission
def create_http_headers():
    """
    根据列表批量新增请求头

    example:
    {
        "workspaceNo": "",
        "templateName": "",
        "templateDesc": "",
        "headerList": [
            {
                "headerName": "",
                "headerValue": "",
                "headerDesc": ""
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('templateName', required=True, nullable=False, help='模板名称不能为空'),
        Argument('templateDesc'),
        Argument('headerList', type=list, required=True, nullable=False, help='请求头列表不能为空')
    ).parse()
    return service.create_http_headers(req)


@blueprint.put('/http/headers')
@require_login
@require_permission
def modify_http_headers():
    """
    根据列表批量修改请求头

    example:
    {
        "templateNo": "",
        "templateName": "",
        "templateDesc": "",
        "headerList": [
            {
                "headerName": "",
                "headerValue": "",
                "headerDesc": ""
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空'),
        Argument('templateName', required=True, nullable=False, help='模板名称不能为空'),
        Argument('templateDesc'),
        Argument('headerList', type=list, required=True, nullable=False, help='请求头列表不能为空')
    ).parse()
    return service.modify_http_headers(req)


@blueprint.delete('/http/headers')
@require_login
@require_permission
def remove_http_headers():
    """
    根据列表批量删除请求头

    example: [1, 2, 3]
    """
    req = ListParser().parse()
    return service.remove_http_headers(req)


@blueprint.post('/http/header/template/duplicate')
@require_login
@require_permission
def duplicate_http_header_template():
    """复制请求头模板"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.duplicate_http_header_template(req)


@blueprint.post('/http/header/template/copy/to/workspace')
@require_login
@require_permission
def copy_http_header_template_to_workspace():
    """复制请求头模板至指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.copy_http_header_template_to_workspace(req)


@blueprint.post('/http/header/template/move/to/workspace')
@require_login
@require_permission
def move_http_header_template_to_workspace():
    """移动请求头模板至指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.move_http_header_template_to_workspace(req)
