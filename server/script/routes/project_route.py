#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.script.routes import blueprint
from server.script.services import project_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/project/list', methods=['GET'])
@require_login
@require_permission
def query_project_list():
    """分页查询测试项目列表
    """
    req = JsonParser(
        Argument('projectNo'),
        Argument('projectName'),
        Argument('projectDesc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_project_list(req)


@blueprint.route('/project/all', methods=['GET'])
@require_login
@require_permission
def query_project_all():
    """查询所有测试项目
    """
    return service.query_project_all()


@blueprint.route('/project', methods=['POST'])
@require_login
@require_permission
def create_project():
    """新增测试项目
    """
    req = JsonParser(
        Argument('projectName', required=True, nullable=False, help='项目名称不能为空'),
        Argument('projectDesc'),
    ).parse()
    return service.create_project(req)


@blueprint.route('/project', methods=['PUT'])
@require_login
@require_permission
def modify_project():
    """修改测试项目
    """
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('projectName', required=True, nullable=False, help='项目名称不能为空'),
        Argument('projectDesc'),
    ).parse()
    return service.modify_project(req)


@blueprint.route('/project', methods=['DELETE'])
@require_login
@require_permission
def delete_project():
    """删除测试项目
    """
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
    ).parse()
    return service.delete_project(req)


@blueprint.route('/project/user', methods=['POST'])
@require_login
@require_permission
def add_project_user():
    """添加测试项目成员
    """
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.add_project_user(req)


@blueprint.route('/project/user', methods=['PUT'])
@require_login
@require_permission
def modify_project_user():
    """修改测试项目成员
    """
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.modify_project_user(req)


@blueprint.route('/project/user', methods=['DELETE'])
@require_login
@require_permission
def remove_project_user():
    """移除测试项目成员
    """
    req = JsonParser(
        Argument('projectNo', required=True, nullable=False, help='项目编号不能为空'),
        Argument('userNoList', required=True, nullable=False, help='用户编号列表不能为空'),
    ).parse()
    return service.remove_project_user(req)
