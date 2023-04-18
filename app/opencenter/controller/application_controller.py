#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : application_controller.py
# @Time    : 2023-04-17 17:14:51
# @Author  : Kelvin.Ye
from app.opencenter.controller import blueprint
from app.opencenter.enum import APPState
from app.opencenter.service import application_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/tpa/list')
@require_login
@require_permission('QUERY_THIRD_PARTY_APP')
def query_tpa_list():
    """分页查询应用列表"""
    req = JsonParser(
        Argument('appNo'),
        Argument('appName'),
        Argument('appCode'),
        Argument('appDesc'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_tpa_list(req)


@blueprint.get('/tpa/info')
@require_login
@require_permission('QUERY_THIRD_PARTY_APP')
def query_tpa_info():
    """查询应用信息"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空')
    ).parse()
    return service.query_tpa_info(req)


@blueprint.post('/tpa')
@require_login
@require_permission('CREATE_THIRD_PARTY_APP')
def create_tpa():
    """新增第三方应用"""
    req = JsonParser(
        Argument('appName', required=True, nullable=False, help='应用名称不能为空'),
        Argument('appCode'),
        Argument('appDesc')
    ).parse()
    return service.create_tpa(req)


@blueprint.put('/tpa')
@require_login
@require_permission('MODIFY_THIRD_PARTY_APP')
def modify_tpa():
    """更新应用信息"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空'),
        Argument('appName', required=True, nullable=False, help='应用名称不能为空'),
        Argument('appCode'),
        Argument('appDesc')
    ).parse()
    return service.modify_tpa(req)


@blueprint.put('/tpa/state')
@require_login
@require_permission('MODIFY_THIRD_PARTY_APP')
def modify_tpa_state():
    """更新应用状态"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空'),
        Argument('state', required=True, nullable=False, enum=APPState, help='应用状态不能为空')
    ).parse()
    return service.modify_tpa_state(req)


@blueprint.post('/tpa/secret/reset')
@require_login
@require_permission('RESET_THIRD_PARTY_APP_SECRET')
def reset_tpa_secret():
    """重置应用密钥"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空')
    ).parse()
    return service.reset_tpa_secret(req)


@blueprint.delete('/tpa')
@require_login
@require_permission('REMOVE_THIRD_PARTY_APP')
def remove_tpa():
    """删除应用"""
    req = JsonParser(
        Argument('appNo', required=True, nullable=False, help='应用编号不能为空')
    ).parse()
    return service.remove_tpa(req)
