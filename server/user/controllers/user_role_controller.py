#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_route
# @Time    : 2020/7/3 15:13
# @Author  : Kelvin.Ye
from server.common.decorators.require import require_login, require_permission
from server.common.parser import JsonParser, Argument
from server.user.controllers import blueprint
from server.user.services import user_role_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/role/rel/list', methods=['GET'])
@require_login
@require_permission
def query_user_role_rel_list():
    """分页查询用户角色关联关系列表
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
        Argument('userName'),
        Argument('roleName'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_user_role_rel_list(req)


@blueprint.route('/role/rel', methods=['POST'])
@require_login
@require_permission
def create_user_role_rel():
    """新增用户角色关联关系
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
    ).parse()
    return service.create_user_role_rel(req)


@blueprint.route('/role/rel', methods=['DELETE'])
@require_login
@require_permission
def delete_user_role_rel():
    """删除用户角色关联关系
    """
    req = JsonParser(
        Argument('userNo'),
        Argument('roleNo'),
    ).parse()
    return service.delete_user_role_rel(req)
