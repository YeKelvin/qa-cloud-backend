#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database_controller.py
# @Time    : 2022-04-04 16:21:55
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.enum import DatabaseType
from app.script.service import database_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/database/engine/list')
@require_login
@require_permission
def query_database_engine_list():
    """分页查询数据库引擎列表"""
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
@require_permission
def query_database_engine_all():
    """查询所有数据库引擎"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('configNo'),
        Argument('configName'),
        Argument('configDesc'),
        Argument('databaseType')
    ).parse()
    return service.query_database_engine_all(req)


@blueprint.get('/database/engine')
@require_login
@require_permission
def query_database_engine_info():
    """查询数据库引擎"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.query_database_engine_info(req)


@blueprint.post('/database/engine')
@require_login
@require_permission
def create_database_engine():
    """新增数据库引擎"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('configName', required=True, nullable=False, help='数据库名称不能为空'),
        Argument('configDesc'),
        Argument('databaseType', required=True, nullable=False, enum=DatabaseType, help='数据库类型不能为空'),
        Argument('variableName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('driverName', required=True, nullable=False, help='驱动名称不能为空'),
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
@require_permission
def modify_database_engine():
    """修改数据库引擎"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空'),
        Argument('configName', required=True, nullable=False, help='数据库名称不能为空'),
        Argument('configDesc'),
        Argument('databaseType', required=True, nullable=False, enum=DatabaseType, help='数据库类型不能为空'),
        Argument('variableName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('driverName', required=True, nullable=False, help='驱动名称不能为空'),
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
@require_permission
def remove_database_engine():
    """删除数据库引擎"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.remove_database_engine(req)


@blueprint.post('/database/engine/duplicate')
@require_login
@require_permission
def duplicate_database_engine():
    """复制数据库引擎"""
    req = JsonParser(
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.duplicate_database_engine(req)


@blueprint.post('/database/engine/copy/to/workspace')
@require_login
@require_permission
def copy_database_engine_to_workspace():
    """复制数据库引擎至指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.copy_database_engine_to_workspace(req)


@blueprint.post('/database/engine/move/to/workspace')
@require_login
@require_permission
def move_database_engine_to_workspace():
    """移动数据库引擎至指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('configNo', required=True, nullable=False, help='数据库编号不能为空')
    ).parse()
    return service.move_database_engine_to_workspace(req)
