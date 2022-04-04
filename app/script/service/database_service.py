#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database_service.py
# @Time    : 2022-04-04 16:22:20
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.script.dao import database_config_dao as DatabaseConfigDao
from app.script.model import TDatabaseConfig
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_database_engine_list(req):
    # 条件分页查询
    pagination = DatabaseConfigDao.select_list(
        workspaceNo=req.workspaceNo,
        databaseNo=req.databaseNo,
        databaseName=req.databaseName,
        databaseDesc=req.databaseDesc,
        databaseType=req.databaseType,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for item in pagination.items:
        data.append({
            'databaseNo': item.DATABASE_NO,
            'databaseName': item.DATABASE_NAME,
            'databaseDesc': item.DATABASE_DESC,
            'databaseType': item.DATABASE_TYPE
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_database_engine_all(req):
    # 条件查询
    items = DatabaseConfigDao.select_all(
        workspaceNo=req.workspaceNo,
        databaseNo=req.databaseNo,
        databaseName=req.databaseName,
        databaseDesc=req.databaseDesc,
        databaseType=req.databaseType
    )

    result = []
    for item in items:
        result.append({
            'databaseNo': item.DATABASE_NO,
            'databaseName': item.DATABASE_NAME,
            'databaseDesc': item.DATABASE_DESC,
            'databaseType': item.DATABASE_TYPE
        })
    return result


@http_service
def create_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        DATABASE_NAME=req.databaseName,
        DATABASE_TYPE=req.databaseType
    )
    check_is_blank(engine, '数据库引擎已存在')

    # 新增数据库引擎
    database_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATABASE_NO=database_no,
        DATABASE_NAME=req.databaseName,
        DATABASE_DESC=req.databaseDesc,
        DATABASE_TYPE=req.databaseType,
        VARIABLE_NAME=req.variableName,
        DRIVER_NAME=req.driverName,
        USERNAME=req.username,
        PASSWORD=req.password,
        HOST=req.host,
        PORT=req.port,
        QUERY=req.query,
        DATABASE=req.database,
        CONNECT_TIMEOUT=req.connectTimeout
    )

    return {'databaseNo': database_no}


@http_service
def modify_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.datasetNo)
    check_is_not_blank(engine, '数据库引擎不存在')

    # 更新数据库引擎信息
    engine.update(
        DATABASE_NAME=req.databaseName,
        DATABASE_DESC=req.databaseDesc,
        DATABASE_TYPE=req.databaseType,
        VARIABLE_NAME=req.variableName,
        DRIVER_NAME=req.driverName,
        USERNAME=req.username,
        PASSWORD=req.password,
        HOST=req.host,
        PORT=req.port,
        QUERY=req.query,
        DATABASE=req.database,
        CONNECT_TIMEOUT=req.connectTimeout
    )


@http_service
def remove_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.databaseNo)
    check_is_not_blank(engine, '数据库引擎不存在')

    # 删除数据库引擎
    engine.delete()


@http_service
def duplicate_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.databaseNo)
    check_is_not_blank(engine, '数据库引擎不存在')

    # 复制数据库引擎
    database_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=engine.WORKSPACE_NO,
        DATABASE_NO=database_no,
        DATABASE_NAME=engine.DATABASE_NAME + ' copy',
        DATABASE_DESC=engine.DATABASE_DESC,
        DATABASE_TYPE=engine.DATABASE_TYPE,
        VARIABLE_NAME=engine.VARIABLE_NAME,
        DRIVER_NAME=engine.DRIVER_NAME,
        USERNAME=engine.USERNAME,
        PASSWORD=engine.PASSWORD,
        HOST=engine.HOST,
        PORT=engine.PORT,
        QUERY=engine.QUERY,
        DATABASE=engine.DATABASE,
        CONNECT_TIMEOUT=engine.CONNECT_TIMEOUT
    )

    return {'databaseNo': database_no}


@http_service
def copy_database_engine_to_workspace(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.databaseNo)
    check_is_not_blank(engine, '数据库引擎不存在')

    # 复制数据库引擎
    database_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATABASE_NO=database_no,
        DATABASE_NAME=engine.DATABASE_NAME + ' copy',
        DATABASE_DESC=engine.DATABASE_DESC,
        DATABASE_TYPE=engine.DATABASE_TYPE,
        VARIABLE_NAME=engine.VARIABLE_NAME,
        DRIVER_NAME=engine.DRIVER_NAME,
        USERNAME=engine.USERNAME,
        PASSWORD=engine.PASSWORD,
        HOST=engine.HOST,
        PORT=engine.PORT,
        QUERY=engine.QUERY,
        DATABASE=engine.DATABASE,
        CONNECT_TIMEOUT=engine.CONNECT_TIMEOUT
    )

    return {'databaseNo': database_no}


@http_service
def move_database_engine_to_workspace(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.databaseNo)
    check_is_not_blank(engine, '数据库引擎不存在')

    engine.update(WORKSPACE_NO=req.workspaceNo)
