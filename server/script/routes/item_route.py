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
def query_item_list():
    """分页查询测试项目列表
    """
    req = JsonParser(
        Argument('itemNo'),
        Argument('itemName'),
        Argument('itemDesc'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_item_list(req)


@blueprint.route('/item/all', methods=['GET'])
@require_login
@require_permission
def query_item_all():
    """查询所有测试项目
    """
    return service.query_item_all()


@blueprint.route('/item', methods=['POST'])
@require_login
@require_permission
def create_item():
    """新增测试项目
    """
    req = JsonParser(
        Argument('itemName', required=True, nullable=False, help='项目名称不能为空'),
        Argument('itemDesc'),
    ).parse()
    return service.create_item(req)


@blueprint.route('/item', methods=['PUT'])
@require_login
@require_permission
def modify_item():
    """修改测试项目
    """
    req = JsonParser(
        Argument('itemNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('itemName', required=True, nullable=False, help='项目名称不能为空'),
        Argument('itemDesc'),
    ).parse()
    return service.modify_item(req)


@blueprint.route('/item', methods=['DELETE'])
@require_login
@require_permission
def delete_item():
    """删除测试项目
    """
    req = JsonParser(
        Argument('itemNo', required=True, nullable=False, help='项目编号不能为空'),
    ).parse()
    return service.delete_item(req)


@blueprint.route('/item/user', methods=['POST'])
@require_login
@require_permission
def add_item_user():
    """添加测试项目成员
    """
    req = JsonParser(
        Argument('itemNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.add_item_user(req)


@blueprint.route('/item/user', methods=['PUT'])
@require_login
@require_permission
def modify_item_user():
    """修改测试项目成员
    """
    req = JsonParser(
        Argument('itemNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.modify_item_user(req)


@blueprint.route('/item/user', methods=['DELETE'])
@require_login
@require_permission
def remove_item_user():
    """移除测试项目成员
    """
    req = JsonParser(
        Argument('itemNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.remove_item_user(req)
