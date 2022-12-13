#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database_controller.py
# @Time    : 2022-04-04 16:21:55
# @Author  : Kelvin.Ye
from app.script.controller import blueprint
from app.script.enum import DatabaseType
from app.script.service import database_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser


log = get_logger(__name__)


@blueprint.get('/database/engine/list')
@require_login
@require_permission('QUERY_DATABASE_ENGINE')
def query_database_engine_list():
    """分页查询数据库配置列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('configNo'),
        Argument('configName'),
        Argument('configDesc'),
        Argument('databaseType'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_database_engine_list(req)


@blueprint.get('/database/engine/all')
@require_login
@require_permission('QUERY_DATABASE_ENGINE')
def query_database_engine_all():
    """查询全部数据库配置"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('databaseType')
    ).parse()
    return service.query_database_engine_all(req)


@blueprint.get('/database/engine/all/in/private')
@require_login
@require_permission('QUERY_DATABASE_ENGINE')
def query_database_engine_all_in_private():
    """根据用户空间查询全部数据库配置"""
    return service.query_database_engine_all_in_private()


@blueprint.get('/database/engine')
@require_login
@require_permission('QUERY_DATABASE_ENGINE')
def query_database_engine_info():
    """查询数据库配置"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.query_database_engine_info(req)


@blueprint.post('/database/engine')
@require_login
@require_permission('CREATE_DATABASE_ENGINE')
def create_database_engine():
    """新增数据库配置"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('configName', required=True, nullable=False, help='数据库名称不能为空'),
        Argument('configDesc'),
        Argument('variableName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('databaseType', required=True, nullable=False, enum=DatabaseType, help='数据库类型不能为空'),
        Argument('username', required=True, nullable=False, help='用户名称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('host', required=True, nullable=False, help='主机不能为空'),
        Argument('port', required=True, nullable=False, help='端号不能为空'),
        Argument('query'),
        Argument('database', required=True, nullable=False, help='库名不能为空'),
        Argument('connectTimeout')
    ).parse()
    return service.create_database_engine(req)


@blueprint.put('/database/engine')
@require_login
@require_permission('MODIFY_DATABASE_ENGINE')
def modify_database_engine():
    """修改数据库配置"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空'),
        Argument('configName', required=True, nullable=False, help='数据库名称不能为空'),
        Argument('configDesc'),
        Argument('variableName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('databaseType', required=True, nullable=False, enum=DatabaseType, help='数据库类型不能为空'),
        Argument('username', required=True, nullable=False, help='用户名称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('host', required=True, nullable=False, help='主机不能为空'),
        Argument('port', required=True, nullable=False, help='端号不能为空'),
        Argument('query'),
        Argument('database', required=True, nullable=False, help='库名不能为空'),
        Argument('connectTimeout')
    ).parse()
    return service.modify_database_engine(req)


@blueprint.delete('/database/engine')
@require_login
@require_permission('REMOVE_DATABASE_ENGINE')
def remove_database_engine():
    """删除数据库配置"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.remove_database_engine(req)


@blueprint.post('/database/engine/duplicate')
@require_login
@require_permission('COPY_DATABASE_ENGINE')
def duplicate_database_engine():
    """复制数据库配置"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.duplicate_database_engine(req)


@blueprint.post('/database/engine/copy/to/workspace')
@require_login
@require_permission('COPY_DATABASE_ENGINE')
def copy_database_engine_to_workspace():
    """复制数据库配置到指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.copy_database_engine_to_workspace(req)


@blueprint.post('/database/engine/move/to/workspace')
@require_login
@require_permission('MOVE_DATABASE_ENGINE')
def move_database_engine_to_workspace():
    """移动数据库配置到指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.move_database_engine_to_workspace(req)
