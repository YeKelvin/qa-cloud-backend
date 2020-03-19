#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : topic_route
# @Time    : 2020/3/13 16:55
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.script.routes import blueprint
from server.script.services import topic_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/topic/list', methods=['GET'])
@require_login
@require_permission
def query_topic_list():
    """分页查询测试主题列表
    """
    req = JsonParser(
        Argument('topicNo'),
        Argument('topicName'),
        Argument('topicDescription'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_topic_list(req)


@blueprint.route('/topic/all', methods=['GET'])
@require_login
@require_permission
def query_topic_all():
    """查询所有测试主题
    """
    return service.query_topic_all()


@blueprint.route('/topic', methods=['POST'])
@require_login
@require_permission
def create_topic():
    """新增测试主题
    """
    req = JsonParser(
        Argument('topicName', required=True, nullable=False, help='主题名称不能为空'),
        Argument('topicDescription'),
    ).parse()
    return service.create_topic(req)


@blueprint.route('/topic', methods=['PUT'])
@require_login
@require_permission
def modify_topic():
    """修改测试主题
    """
    req = JsonParser(
        Argument('topicNo', required=True, nullable=False, help='主题编号不能为空'),
        Argument('topicName', required=True, nullable=False, help='主题名称不能为空'),
        Argument('topicDescription'),
    ).parse()
    return service.modify_topic(req)


@blueprint.route('/topic', methods=['DELETE'])
@require_login
@require_permission
def delete_topic():
    """删除测试主题
    """
    req = JsonParser(
        Argument('topicNo', required=True, nullable=False, help='主题编号不能为空'),
    ).parse()
    return service.delete_topic(req)
