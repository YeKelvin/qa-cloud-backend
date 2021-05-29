#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_header_route
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controllers import blueprint
from app.script.services import http_header_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/http/header/list')
@require_login
@require_permission
def query_http_header_list():
    """分页查询 HTTP头部列表
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_http_header_list(req)


@blueprint.get('/http/header/all')
@require_login
@require_permission
def query_http_header_all():
    """查询所有 HTTP头部
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.query_http_header_all(req)


@blueprint.post('/http/header')
@require_login
@require_permission
def create_http_header():
    """新增 HTTP头部
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.create_http_header(req)


@blueprint.put('/http/header')
@require_login
@require_permission
def modify_http_header():
    """修改 HTTP头部
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.modify_http_header(req)


@blueprint.delete('/http/header')
@require_login
@require_permission
def delete_http_header():
    """删除 HTTP头部
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.delete_http_header(req)
