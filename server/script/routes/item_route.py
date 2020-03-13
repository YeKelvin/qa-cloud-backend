#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.script.routes import blueprint
from server.script.services import item_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/item/list', methods=['GET'])
@require_login
@require_permission
def item_list():
    """分页查询测试项目列表
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.item_list(req)


@blueprint.route('/item/all', methods=['GET'])
@require_login
@require_permission
def item_all():
    """查询所有测试项目
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.item_all(req)


@blueprint.route('/item', methods=['POST'])
@require_login
@require_permission
def create_item():
    """新增测试项目
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.create_item(req)


@blueprint.route('/item', methods=['PUT'])
@require_login
@require_permission
def modify_item():
    """修改测试项目
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.modify_item(req)


@blueprint.route('/item', methods=['DELETE'])
@require_login
@require_permission
def delete_item():
    """删除测试项目
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.delete_item(req)
