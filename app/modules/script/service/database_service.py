#!/usr/bin/ python3
# @File    : database_service.py
# @Time    : 2022-04-04 16:22:20
# @Author  : Kelvin.Ye
from app.modules.script.dao import database_config_dao
from app.modules.script.model import TDatabaseConfig
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_database_engine_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TDatabaseConfig.WORKSPACE_NO, req.workspaceNo)
    conds.like(TDatabaseConfig.DATABASE_NO, req.dbNo)
    conds.like(TDatabaseConfig.DATABASE_NAME, req.dbName)
    conds.like(TDatabaseConfig.DATABASE_DESC, req.dbDesc)
    conds.like(TDatabaseConfig.DATABASE_TYPE, req.dbType)

    # 分页查询
    pagination = (
        TDatabaseConfig
        .filter(*conds)
        .order_by(TDatabaseConfig.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'dbNo': item.DATABASE_NO,
            'dbName': item.DATABASE_NAME,
            'dbDesc': item.DATABASE_DESC,
            'dbType': item.DATABASE_TYPE
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_database_engine_all(req):
    conds = QueryCondition()
    conds.like(TDatabaseConfig.WORKSPACE_NO, req.workspaceNo)
    conds.like(TDatabaseConfig.DATABASE_NO, req.dbType)

    items = TDatabaseConfig.filter(*conds).order_by(TDatabaseConfig.CREATED_TIME.desc()).all()

    return [
        {
            'dbNo': item.DATABASE_NO,
            'dbName': item.DATABASE_NAME,
            'dbDesc': item.DATABASE_DESC,
            'dbType': item.DATABASE_TYPE
        }
        for item in items
    ]


@http_service
def query_database_engine_info(req):
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(req.dbNo)
    check_exists(engine, error_msg='数据库引擎不存在')

    return {
        'dbNo': engine.DATABASE_NO,
        'dbName': engine.DATABASE_NAME,
        'dbDesc': engine.DATABASE_DESC,
        'dbType': engine.DATABASE_TYPE,
        'username': engine.USERNAME,
        'password': engine.PASSWORD,
        'host': engine.HOST,
        'port': engine.PORT,
        'query': engine.QUERY,
        'database': engine.DATABASE,
        'variableName': engine.VARIABLE_NAME,
        'connectTimeout': engine.CONNECT_TIMEOUT
    }


@http_service
def create_database_engine(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 唯一性校验
    engine = database_config_dao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        DATABASE_NAME=req.dbName,
        DATABASE_TYPE=req.dbType
    )
    check_not_exists(engine, error_msg='数据库引擎已存在')

    # 新增数据库引擎
    db_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATABASE_NO=db_no,
        DATABASE_NAME=req.dbName,
        DATABASE_DESC=req.dbDesc,
        DATABASE_TYPE=req.dbType,
        USERNAME=req.username,
        PASSWORD=req.password,
        HOST=req.host,
        PORT=req.port,
        QUERY=req.query,
        DATABASE=req.database,
        VARIABLE_NAME=req.variableName,
        CONNECT_TIMEOUT=req.connectTimeout
    )

    return {'dbNo': db_no}


@http_service
def modify_database_engine(req):
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(req.dbNo)
    check_exists(engine, error_msg='数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 更新数据库引擎信息
    engine.update(
        DATABASE_NAME=req.dbName,
        DATABASE_DESC=req.dbDesc,
        DATABASE_TYPE=req.dbType,
        USERNAME=req.username,
        PASSWORD=req.password,
        HOST=req.host,
        PORT=req.port,
        QUERY=req.query,
        DATABASE=req.database,
        VARIABLE_NAME=req.variableName,
        CONNECT_TIMEOUT=req.connectTimeout
    )


@http_service
def remove_database_engine(req):
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(req.dbNo)
    check_exists(engine, error_msg='数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 删除数据库引擎
    engine.delete()


@http_service
def duplicate_database_engine(req):
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(req.dbNo)
    check_exists(engine, error_msg='数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 复制数据库引擎
    db_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=engine.WORKSPACE_NO,
        DATABASE_NO=db_no,
        DATABASE_NAME=engine.DATABASE_NAME,
        DATABASE_DESC=engine.DATABASE_DESC,
        DATABASE_TYPE=engine.DATABASE_TYPE,
        USERNAME=engine.USERNAME,
        PASSWORD=engine.PASSWORD,
        HOST=engine.HOST,
        PORT=engine.PORT,
        QUERY=engine.QUERY,
        DATABASE=engine.DATABASE,
        VARIABLE_NAME=engine.VARIABLE_NAME,
        CONNECT_TIMEOUT=engine.CONNECT_TIMEOUT
    )

    return {'dbNo': db_no}


@http_service
def copy_database_engine_to_workspace(req):
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(req.dbNo)
    check_exists(engine, error_msg='数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 复制数据库引擎
    db_no = new_id()
    TDatabaseConfig.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATABASE_NO=db_no,
        DATABASE_NAME=engine.DATABASE_NAME,
        DATABASE_DESC=engine.DATABASE_DESC,
        DATABASE_TYPE=engine.DATABASE_TYPE,
        USERNAME=engine.USERNAME,
        PASSWORD=engine.PASSWORD,
        HOST=engine.HOST,
        PORT=engine.PORT,
        QUERY=engine.QUERY,
        DATABASE=engine.DATABASE,
        VARIABLE_NAME=engine.VARIABLE_NAME,
        CONNECT_TIMEOUT=engine.CONNECT_TIMEOUT
    )

    return {'dbNo': db_no}


@http_service
def move_database_engine_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(req.dbNo)
    check_exists(engine, error_msg='数据库引擎不存在')
    # 移动数据库引擎
    engine.update(WORKSPACE_NO=req.workspaceNo)
