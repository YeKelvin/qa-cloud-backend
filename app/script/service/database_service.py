#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database_service.py
# @Time    : 2022-04-04 16:22:20
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.id_generator import new_id
from app.common.validator import check_exists
from app.common.validator import check_not_exists
from app.common.validator import check_workspace_permission
from app.script.dao import database_config_dao as DatabaseConfigDao
from app.script.model import TDatabaseConfig
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_database_engine_list(req):
    # 条件分页查询
    pagination = DatabaseConfigDao.select_list(
        workspaceNo=req.workspaceNo,
        configNo=req.configNo,
        configName=req.configName,
        configDesc=req.configDesc,
        databaseType=req.databaseType,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for item in pagination.items:
        data.append({
            'configNo': item.CONFIG_NO,
            'configName': item.CONFIG_NAME,
            'configDesc': item.CONFIG_DESC,
            'databaseType': item.DATABASE_TYPE
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_database_engine_all(req):
    # 条件查询
    items = DatabaseConfigDao.select_all(
        workspaceNo=req.workspaceNo,
        configNo=req.configNo,
        configName=req.configName,
        configDesc=req.configDesc,
        databaseType=req.databaseType
    )

    result = []
    for item in items:
        result.append({
            'configNo': item.CONFIG_NO,
            'configName': item.CONFIG_NAME,
            'configDesc': item.CONFIG_DESC,
            'databaseType': item.DATABASE_TYPE
        })
    return result


@http_service
def query_database_engine_info(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, '数据库引擎不存在')

    return {
        'configNo': engine.CONFIG_NO,
        'configName': engine.CONFIG_NAME,
        'configDesc': engine.CONFIG_DESC,
        'variableName': engine.VARIABLE_NAME,
        'databaseType': engine.DATABASE_TYPE,
        'username': engine.USERNAME,
        'password': engine.PASSWORD,
        'host': engine.HOST,
        'port': engine.PORT,
        'query': engine.QUERY,
        'database': engine.DATABASE,
        'connectTimeout': engine.CONNECT_TIMEOUT
    }


@http_service
@transactional
def create_database_engine(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 唯一性校验
    engine = DatabaseConfigDao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        CONFIG_NAME=req.configName,
        DATABASE_TYPE=req.databaseType
    )
    check_not_exists(engine, '数据库引擎已存在')

    # 新增数据库引擎
    config_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=req.workspaceNo,
        CONFIG_NO=config_no,
        CONFIG_NAME=req.configName,
        CONFIG_DESC=req.configDesc,
        VARIABLE_NAME=req.variableName,
        DATABASE_TYPE=req.databaseType,
        USERNAME=req.username,
        PASSWORD=req.password,
        HOST=req.host,
        PORT=req.port,
        QUERY=req.query,
        DATABASE=req.database,
        CONNECT_TIMEOUT=req.connectTimeout
    )

    return {'configNo': config_no}


@http_service
@transactional
def modify_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, '数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 更新数据库引擎信息
    engine.update(
        CONFIG_NAME=req.configName,
        CONFIG_DESC=req.configDesc,
        VARIABLE_NAME=req.variableName,
        DATABASE_TYPE=req.databaseType,
        USERNAME=req.username,
        PASSWORD=req.password,
        HOST=req.host,
        PORT=req.port,
        QUERY=req.query,
        DATABASE=req.database,
        CONNECT_TIMEOUT=req.connectTimeout
    )


@http_service
@transactional
def remove_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, '数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 删除数据库引擎
    engine.delete()


@http_service
@transactional
def duplicate_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, '数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 复制数据库引擎
    config_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=engine.WORKSPACE_NO,
        CONFIG_NO=config_no,
        CONFIG_NAME=f'{engine.CONFIG_NAME} copy',
        CONFIG_DESC=engine.CONFIG_DESC,
        VARIABLE_NAME=engine.VARIABLE_NAME,
        DATABASE_TYPE=engine.DATABASE_TYPE,
        USERNAME=engine.USERNAME,
        PASSWORD=engine.PASSWORD,
        HOST=engine.HOST,
        PORT=engine.PORT,
        QUERY=engine.QUERY,
        DATABASE=engine.DATABASE,
        CONNECT_TIMEOUT=engine.CONNECT_TIMEOUT
    )

    return {'configNo': config_no}


@http_service
@transactional
def copy_database_engine_to_workspace(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, '数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 复制数据库引擎
    config_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=req.workspaceNo,
        CONFIG_NO=config_no,
        CONFIG_NAME=f'{engine.CONFIG_NAME} copy',
        CONFIG_DESC=engine.CONFIG_DESC,
        VARIABLE_NAME=engine.VARIABLE_NAME,
        DATABASE_TYPE=engine.DATABASE_TYPE,
        USERNAME=engine.USERNAME,
        PASSWORD=engine.PASSWORD,
        HOST=engine.HOST,
        PORT=engine.PORT,
        QUERY=engine.QUERY,
        DATABASE=engine.DATABASE,
        CONNECT_TIMEOUT=engine.CONNECT_TIMEOUT
    )

    return {'configNo': config_no}


@http_service
@transactional
def move_database_engine_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, '数据库引擎不存在')
    # 移动数据库引擎
    engine.update(WORKSPACE_NO=req.workspaceNo)
