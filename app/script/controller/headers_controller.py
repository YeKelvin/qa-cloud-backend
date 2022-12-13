#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : headers_controller.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.script.controller import blueprint
from app.script.service import headers_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.parser import ListParser


log = get_logger(__name__)


@blueprint.get('/httpheader/template/list')
@require_login
@require_permission('QUERY_HTTPHEADER_TEMPLATE')
def query_httpheader_template_list():
    """分页查询请求头模板列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('templateNo'),
        Argument('templateName'),
        Argument('templateDesc'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_httpheader_template_list(req)


@blueprint.get('/httpheader/template/all')
@require_login
@require_permission('QUERY_HTTPHEADER_TEMPLATE')
def query_httpheader_template_all():
    """查询全部请求头模板"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_httpheader_template_all(req)


@blueprint.get('/httpheader/template/all/in/private')
@require_login
@require_permission('QUERY_HTTPHEADER_TEMPLATE')
def query_httpheader_template_all_in_private():
    """根据用户空间查询全部请求头模板"""
    return service.query_httpheader_template_all_in_private()


@blueprint.post('/httpheader/template')
@require_login
@require_permission('CREATE_HTTPHEADER_TEMPLATE')
def create_httpheader_template():
    """新增请求头模板"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('templateName', required=True, nullable=False, help='模板名称不能为空'),
        Argument('templateDesc')
    ).parse()
    return service.create_httpheader_template(req)


@blueprint.put('/httpheader/template')
@require_login
@require_permission('MODIFY_HTTPHEADER_TEMPLATE')
def modify_httpheader_template():
    """修改请求头模板"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空'),
        Argument('templateName', required=True, nullable=False, help='模板名称不能为空'),
        Argument('templateDesc')
    ).parse()
    return service.modify_httpheader_template(req)


@blueprint.delete('/httpheader/template')
@require_login
@require_permission('REMOVE_HTTPHEADER_TEMPLATE')
def remove_httpheader_template():
    """删除请求头模板"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.remove_httpheader_template(req)


@blueprint.post('/http/header')
@require_login
@require_permission('CREATE_HTTP_HEADER')
def create_http_header():
    """新增请求头"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空'),
        Argument('headerName', required=True, nullable=False, help='请求头名称不能为空'),
        Argument('headerValue', required=True, nullable=False, help='请求头值不能为空'),
        Argument('headerDesc')
    ).parse()
    return service.create_http_header(req)


@blueprint.put('/http/header')
@require_login
@require_permission('MODIFY_HTTP_HEADER')
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
@require_permission('REMOVE_HTTP_HEADER')
def remove_http_header():
    """删除请求头"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空')
    ).parse()
    return service.remove_http_header(req)


@blueprint.patch('/http/header/enable')
@require_login
@require_permission('MODIFY_HTTP_HEADER')
def enable_http_header():
    """启用变量"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空')
    ).parse()
    return service.enable_http_header(req)


@blueprint.patch('/http/header/disable')
@require_login
@require_permission('MODIFY_HTTP_HEADER')
def disable_http_header():
    """禁用变量"""
    req = JsonParser(
        Argument('headerNo', required=True, nullable=False, help='请求头编号不能为空')
    ).parse()
    return service.disable_http_header(req)


@blueprint.get('/http/headers/by/template')
@require_login
@require_permission('QUERY_HTTP_HEADER')
def query_http_headers_by_template():
    """根据模板查询全部请求头"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.query_http_headers_by_template(req)


@blueprint.get('/http/headers')
@require_login
@require_permission('QUERY_HTTP_HEADER')
def query_http_headers():
    """根据列表批量查询请求头"""
    req = ListParser().parse()
    return service.query_http_headers(req)


@blueprint.post('/http/headers')
@require_login
@require_permission('CREATE_HTTP_HEADER')
def create_http_headers():
    """
    根据列表批量新增请求头

    example:
    {
        "templateNo": "",
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
        Argument('headerList', type=list, required=True, nullable=False, help='请求头列表不能为空')
    ).parse()
    return service.create_http_headers(req)


@blueprint.put('/http/headers')
@require_login
@require_permission('MODIFY_HTTP_HEADER')
def modify_http_headers():
    """
    根据列表批量修改请求头

    example:
    {
        "templateNo": "",
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
        Argument('headerList', type=list, required=True, nullable=False, help='请求头列表不能为空')
    ).parse()
    return service.modify_http_headers(req)


@blueprint.delete('/http/headers')
@require_login
@require_permission('REMOVE_HTTP_HEADER')
def remove_http_headers():
    """批量删除请求头"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空'),
        Argument('headerNos', type=list, required=True, nullable=False, help='请求头列表不能为空')
    ).parse()
    return service.remove_http_headers(req)


@blueprint.post('/httpheader/template/duplicate')
@require_login
@require_permission('COPY_HTTPHEADER_TEMPLATE')
def duplicate_httpheader_template():
    """复制请求头模板"""
    req = JsonParser(
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.duplicate_httpheader_template(req)


@blueprint.post('/httpheader/template/copy/to/workspace')
@require_login
@require_permission('COPY_HTTPHEADER_TEMPLATE')
def copy_httpheader_template_to_workspace():
    """复制请求头模板到指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.copy_httpheader_template_to_workspace(req)


@blueprint.post('/httpheader/template/move/to/workspace')
@require_login
@require_permission('MOVE_HTTPHEADER_TEMPLATE')
def move_httpheader_template_to_workspace():
    """移动请求头模板到指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('templateNo', required=True, nullable=False, help='模板编号不能为空')
    ).parse()
    return service.move_httpheader_template_to_workspace(req)
