#!/usr/bin/ python3
# @File    : database_service.py
# @Time    : 2022-04-04 16:22:20
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.modules.public.enum import WorkspaceScope
from app.modules.public.model import TWorkspace
from app.modules.public.model import TWorkspaceUser
from app.modules.script.dao import database_config_dao as DatabaseConfigDao
from app.modules.script.model import TDatabaseConfig
from app.tools import localvars
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.identity import new_id
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_database_engine_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TDatabaseConfig.WORKSPACE_NO, req.workspaceNo)
    conds.like(TDatabaseConfig.CONFIG_NO, req.configNo)
    conds.like(TDatabaseConfig.CONFIG_NAME, req.configName)
    conds.like(TDatabaseConfig.CONFIG_DESC, req.configDesc)
    conds.like(TDatabaseConfig.DATABASE_TYPE, req.databaseType)

    # 分页查询
    pagination = (
        TDatabaseConfig
        .filter(*conds)
        .order_by(TDatabaseConfig.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize)
    )

    data = [
        {
            'configNo': item.CONFIG_NO,
            'configName': item.CONFIG_NAME,
            'configDesc': item.CONFIG_DESC,
            'databaseType': item.DATABASE_TYPE
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_database_engine_all(req):
    conds = QueryCondition()
    conds.like(TDatabaseConfig.WORKSPACE_NO, req.workspaceNo)
    conds.like(TDatabaseConfig.CONFIG_NO, req.databaseType)

    items = TDatabaseConfig.filter(*conds).order_by(TDatabaseConfig.CREATED_TIME.desc()).all()

    return [
        {
            'configNo': item.CONFIG_NO,
            'configName': item.CONFIG_NAME,
            'configDesc': item.CONFIG_DESC,
            'databaseType': item.DATABASE_TYPE
        }
        for item in items
    ]


@http_service
def query_database_engine_all_in_private():
    # 公共空间条件查询
    public_conds = QueryCondition(TWorkspace, TDatabaseConfig)
    public_conds.equal(TWorkspace.WORKSPACE_NO, TDatabaseConfig.WORKSPACE_NO)
    public_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PUBLIC.value)
    public_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TDatabaseConfig.CONFIG_NO,
            TDatabaseConfig.CONFIG_NAME,
            TDatabaseConfig.CONFIG_DESC,
            TDatabaseConfig.DATABASE_TYPE
        )
        .filter(*public_conds)
    )

    # 保护空间条件查询
    protected_conds = QueryCondition(TWorkspace, TWorkspaceUser, TDatabaseConfig)
    protected_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_NO, TDatabaseConfig.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PROTECTED.value)
    protected_conds.equal(TWorkspaceUser.USER_NO, localvars.get_user_no())
    protected_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TDatabaseConfig.CONFIG_NO,
            TDatabaseConfig.CONFIG_NAME,
            TDatabaseConfig.CONFIG_DESC,
            TDatabaseConfig.DATABASE_TYPE
        )
        .filter(*protected_conds)
    )

    # 私人空间条件查询
    private_conds = QueryCondition(TWorkspace, TWorkspaceUser, TDatabaseConfig)
    private_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_NO, TDatabaseConfig.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PRIVATE.value)
    private_conds.equal(TWorkspaceUser.USER_NO, localvars.get_user_no())
    private_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TDatabaseConfig.CONFIG_NO,
            TDatabaseConfig.CONFIG_NAME,
            TDatabaseConfig.CONFIG_DESC,
            TDatabaseConfig.DATABASE_TYPE
        )
        .filter(*private_conds)
    )

    items = (
        public_filter
        .union(protected_filter)
        .union(private_filter)
        .order_by(TWorkspace.WORKSPACE_SCOPE.desc())
        .all()
    )

    return [
        {
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'configNo': item.CONFIG_NO,
            'configName': item.CONFIG_NAME,
            'configDesc': item.CONFIG_DESC,
            'databaseType': item.DATABASE_TYPE
        }
        for item in items
    ]


@http_service
def query_database_engine_info(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, error_msg='数据库引擎不存在')

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
    check_not_exists(engine, error_msg='数据库引擎已存在')

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
    check_exists(engine, error_msg='数据库引擎不存在')

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
    check_exists(engine, error_msg='数据库引擎不存在')

    # 校验空间权限
    check_workspace_permission(engine.WORKSPACE_NO)

    # 删除数据库引擎
    engine.delete()


@http_service
@transactional
def duplicate_database_engine(req):
    # 查询数据库引擎
    engine = DatabaseConfigDao.select_by_no(req.configNo)
    check_exists(engine, error_msg='数据库引擎不存在')

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
    check_exists(engine, error_msg='数据库引擎不存在')

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
    check_exists(engine, error_msg='数据库引擎不存在')
    # 移动数据库引擎
    engine.update(WORKSPACE_NO=req.workspaceNo)
