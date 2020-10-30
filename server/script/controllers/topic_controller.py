#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : topic_route
# @Time    : 2020/3/13 16:55
# @Author  : Kelvin.Ye
from server.common.decorators.require import require_login, require_permission
from server.common.parser import JsonParser, Argument
from server.script.controllers import blueprint
from server.script.services import topic_service as service
from server.common.utils.log_util import get_logger

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
        Argument('topicDesc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
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
        Argument('topicDesc'),
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
        Argument('topicDesc'),
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


@blueprint.route('/topic/collection', methods=['POST'])
@require_login
@require_permission
def add_topic_collection():
    """添加测试主题下的集合
    """
    req = JsonParser(
        Argument('topicNo', required=True, nullable=False, help='主题编号不能为空'),
        Argument('collectionNoList', required=True, nullable=False, help='集合编号列表不能为空'),
    ).parse()
    return service.add_topic_collection(req)


@blueprint.route('/topic/collection', methods=['PUT'])
@require_login
@require_permission
def modify_topic_collection():
    """修改测试主题下的集合
    """
    req = JsonParser(
        Argument('topicNo', required=True, nullable=False, help='主题编号不能为空'),
        Argument('collectionNoList', required=True, nullable=False, help='集合编号列表不能为空'),
    ).parse()
    return service.modify_topic_collection(req)


@blueprint.route('/topic/collection', methods=['DELETE'])
@require_login
@require_permission
def remove_topic_collection():
    """移除测试主题下的集合
    """
    req = JsonParser(
        Argument('topicNo', required=True, nullable=False, help='主题编号不能为空'),
        Argument('collectionNoList', required=True, nullable=False, help='集合编号列表不能为空'),
    ).parse()
    return service.remove_topic_collection(req)
