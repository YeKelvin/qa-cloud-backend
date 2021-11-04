#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : command.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from app.common.id_generator import new_id
from app.extension import db
from app.script.model import TVariableDataset
from app.system.model import TActionLog
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUserRel
from app.user.model import TPermission
from app.user.model import TRole
from app.user.model import TRolePermissionRel
from app.user.model import TUser
from app.user.model import TUserLoginInfo
from app.user.model import TUserPassword
from app.user.model import TUserRoleRel
from app.utils.log_util import get_logger
from app.utils.security import encrypt_password


from app.script.model import *  # noqa isort:skip
from app.system.model import *  # noqa isort:skip
from app.public.model import *  # noqa isort:skip
from app.user.model import *  # noqa isort:skip


log = get_logger(__name__)


@click.command()
@click.option('-d', '--drop', default=False, help='初始化数据库前是否先删除所有表，默认False')
@with_appcontext
def initdb(drop):
    """创建表"""
    if drop:
        db.drop_all()
        click.echo('删除所有数据库表成功')
    db.create_all()
    click.echo('创建所有数据库表成功')


@click.command()
def initdata():
    """初始化数据"""
    init_user()
    init_role()
    init_permission()
    init_user_role_rel()
    init_role_permission_rel()
    init_script_global_variable_set()
    init_action_log()
    click.echo('初始化数据成功')


@with_appcontext
def init_user():
    """初始化用户"""
    user_no = new_id()
    TUser.insert(USER_NO=user_no, USER_NAME='超级管理员', STATE='ENABLE')
    TUserLoginInfo.insert(USER_NO=user_no, LOGIN_NAME='admin', LOGIN_TYPE='ACCOUNT')
    TUserPassword.insert(
        USER_NO=user_no,
        PASSWORD=encrypt_password('admin', 'admin'),
        PASSWORD_TYPE='LOGIN',
        ERROR_TIMES=0,
        CREATE_TYPE='CUSTOMER'
    )

    worksapce_no = new_id()
    TWorkspace.insert(
        WORKSPACE_NO=worksapce_no,
        WORKSPACE_NAME='超级管理员的私有空间',
        WORKSPACE_SCOPE='PRIVATE'
    )
    TWorkspaceUserRel.insert(WORKSPACE_NO=worksapce_no, USER_NO=user_no)

    click.echo('创建 admin用户成功')


@with_appcontext
def init_role():
    """初始化角色"""
    _create_role(name='SuperAdmin', role_desc='超级管理员')
    _create_role(name='Admin', role_desc='管理员')
    _create_role(name='Leader', role_desc='组长')
    _create_role(name='General', role_desc='用户')

    click.echo('创建角色成功')


@with_appcontext
def init_permission():
    """初始化权限"""
    # user模块路由
    _create_permission(name='用户登录', method='POST', endpoint='/user/login')
    _create_permission(name='用户登出', method='POST', endpoint='/user/logout')
    _create_permission(name='用户注册', method='POST', endpoint='/user/register')
    _create_permission(name='重置密码', method='PATCH', endpoint='/user/password/reset')
    _create_permission(name='查询用户信息', method='GET', endpoint='/user/info')
    _create_permission(name='分页查询用户列表', method='GET', endpoint='/user/list')
    _create_permission(name='查询所有用户', method='GET', endpoint='/user/all')
    _create_permission(name='更新用户信息', method='PUT', endpoint='/user/info')
    _create_permission(name='更新用户状态', method='PATCH', endpoint='/user/info/state')
    _create_permission(name='删除用户', method='DELETE', endpoint='/user')
    _create_permission(name='分页查询权限列表', method='GET', endpoint='/user/permission/list')
    _create_permission(name='查询所有权限', method='GET', endpoint='/user/permission/all')
    _create_permission(name='新增权限', method='POST', endpoint='/user/permission')
    _create_permission(name='更新权限信息', method='PUT', endpoint='/user/permission')
    _create_permission(name='更新权限状态', method='PATCH', endpoint='/user/permission/state')
    _create_permission(name='删除权限', method='DELETE', endpoint='/user/permission')
    _create_permission(name='分页查询角色列表', method='GET', endpoint='/user/role/list')
    _create_permission(name='查询所有角色', method='GET', endpoint='/user/role/all')
    _create_permission(name='新增角色', method='POST', endpoint='/user/role')
    _create_permission(name='更新角色信息', method='PUT', endpoint='/user/role')
    _create_permission(name='更新角色状态', method='PATCH', endpoint='/user/role/state')
    _create_permission(name='删除角色', method='DELETE', endpoint='/user/role')
    _create_permission(name='分页查询用户角色关联列表', method='GET', endpoint='/user/role/rel/list')
    _create_permission(name='新增用户角色关联', method='POST', endpoint='/user/role/rel')
    _create_permission(name='删除用户角色关联', method='DELETE', endpoint='/user/role/rel')
    _create_permission(name='分页查询角色权限关联列表', method='GET', endpoint='/user/role/permission/rel/list')
    _create_permission(name='新增角色权限关联', method='POST', endpoint='/user/role/permission/rel')
    _create_permission(name='删除角色权限关联', method='DELETE', endpoint='/user/role/permission/rel')

    # system模块路由
    # log
    _create_permission(name='分页查询操作日志列表', method='GET', endpoint='/system/action/log/list')

    # public模块路由
    # workspace
    _create_permission(name='分页查询工作空间列表', method='GET', endpoint='/public/workspace/list')
    _create_permission(name='查询所有工作空间', method='GET', endpoint='/public/workspace/all')
    _create_permission(name='新增工作空间', method='POST', endpoint='/public/workspace')
    _create_permission(name='修改工作空间', method='PUT', endpoint='/public/workspace')
    _create_permission(name='删除工作空间', method='DELETE', endpoint='/public/workspace')
    _create_permission(name='分页查询空间成员列表', method='GET', endpoint='/public/workspace/user/list')
    _create_permission(name='查询所有空间成员', method='GET', endpoint='/public/workspace/user/all')
    _create_permission(name='修改空间成员', method='PUT', endpoint='/public/workspace/user')

    # tag
    _create_permission(name='分页查询标签列表', method='GET', endpoint='/public/tag/list')
    _create_permission(name='查询所有标签', method='GET', endpoint='/public/tag/all')
    _create_permission(name='新增标签', method='POST', endpoint='/public/tag')
    _create_permission(name='修改标签', method='PUT', endpoint='/public/tag')
    _create_permission(name='删除标签', method='DELETE', endpoint='/public/tag')

    # script模块路由
    # element
    _create_permission(name='分页查询元素列表', method='GET', endpoint='/script/element/list')
    _create_permission(name='查询所有元素', method='GET', endpoint='/script/element/all')
    _create_permission(name='查询元素信息', method='GET', endpoint='/script/element/info')
    _create_permission(name='查询元素子代', method='GET', endpoint='/script/element/children')
    _create_permission(name='根据元素编号列表查询元素子代', method='GET', endpoint='/script/elements/children')
    _create_permission(name='新增元素', method='POST', endpoint='/script/element')
    _create_permission(name='修改元素', method='PUT', endpoint='/script/element')
    _create_permission(name='删除元素', method='DELETE', endpoint='/script/element')
    _create_permission(name='启用元素', method='PATCH', endpoint='/script/element/enable')
    _create_permission(name='禁用元素', method='PATCH', endpoint='/script/element/disable')
    _create_permission(name='根据父元素编号新增子代元素', method='POST', endpoint='/script/element/children')
    _create_permission(name='上移元素', method='PATCH', endpoint='/script/element/move/up')
    _create_permission(name='下移元素', method='PATCH', endpoint='/script/element/move/down')
    _create_permission(name='移动元素', method='POST', endpoint='/script/element/move')
    _create_permission(name='复制元素及其子代', method='POST', endpoint='/script/element/duplicate')
    _create_permission(name='查询元素关联的HTTP请求头模板列表', method='GET', endpoint='/script/element/http/headers/template/list')
    _create_permission(name='批量新增元素和HTTP请求头模板的关联', method='POST', endpoint='/script/element/http/headers/template/list')
    _create_permission(name='修改元素关联的HTTP请求头模板关联列表', method='PUT', endpoint='/script/element/http/headers/template/list')
    _create_permission(name='查询内置元素', method='GET', endpoint='/script/element/builtin/children')
    _create_permission(name='新增内置元素', method='POST', endpoint='/script/element/builtin/children')
    _create_permission(name='修改内置元素', method='PUT', endpoint='/script/element/builtin/children')
    _create_permission(name='剪贴元素', method='POST', endpoint='/script/element/paste')

    # execution
    _create_permission(name='执行集合', method='POST', endpoint='/script/execute/collection')
    _create_permission(name='执行分组', method='POST', endpoint='/script/execute/group')
    _create_permission(name='执行取样器', method='POST', endpoint='/script/execute/sampler')
    _create_permission(name='执行片段集合', method='POST', endpoint='/script/execute/snippet/collection')
    _create_permission(name='执行片段取样器', method='POST', endpoint='/script/execute/snippet/sampler')
    _create_permission(name='执行测试计划', method='POST', endpoint='/script/execute/testplan')

    # variables
    _create_permission(name='分页查询变量集列表', method='GET', endpoint='/script/variable/dataset/list')
    _create_permission(name='查询所有变量集', method='GET', endpoint='/script/variable/dataset/all')
    _create_permission(name='新增变量集', method='POST', endpoint='/script/variable/dataset')
    _create_permission(name='修改变量集', method='PUT', endpoint='/script/variable/dataset')
    _create_permission(name='删除变量集', method='DELETE', endpoint='/script/variable/dataset')
    _create_permission(name='新增变量', method='POST', endpoint='/script/variable')
    _create_permission(name='修改变量', method='PUT', endpoint='/script/variable')
    _create_permission(name='删除变量', method='DELETE', endpoint='/script/variable')
    _create_permission(name='启用变量', method='PATCH', endpoint='/script/variable/enable')
    _create_permission(name='禁用变量', method='PATCH', endpoint='/script/variable/disable')
    _create_permission(name='更新变量当前值', method='PATCH', endpoint='/script/variable/current/value')
    _create_permission(name='查询变量集下的变量', method='GET', endpoint='/script/variables/by/set')
    _create_permission(name='根据列表查询变量', method='GET', endpoint='/script/variables')
    _create_permission(name='根据列表批量新增变量', method='POST', endpoint='/script/variables')
    _create_permission(name='根据列表批量修改变量', method='PUT', endpoint='/script/variables')
    _create_permission(name='根据列表批量删除变量', method='DELETE', endpoint='/script/variables')
    _create_permission(name='复制变量集', method='POST', endpoint='/script/variable/dataset/duplicate')
    _create_permission(name='复制变量集至指定工作空间', method='POST', endpoint='/script/variable/dataset/copy/to/workspace')
    _create_permission(name='移动变量集至指定工作空间', method='PATCH', endpoint='/script/variable/dataset/move/to/workspace')

    # headers
    _create_permission(name='分页查询请求头模板列表', method='GET', endpoint='/script/http/headers/template/list')
    _create_permission(name='查询所有请求头模板', method='GET', endpoint='/script/http/headers/template/all')
    _create_permission(name='新增请求头模板', method='POST', endpoint='/script/http/headers/template')
    _create_permission(name='修改请求头模板', method='PUT', endpoint='/script/http/headers/template')
    _create_permission(name='删除请求头模板', method='DELETE', endpoint='/script/http/headers/template')
    _create_permission(name='新增请求头', method='POST', endpoint='/script/http/header')
    _create_permission(name='修改请求头', method='PUT', endpoint='/script/http/header')
    _create_permission(name='删除请求头', method='DELETE', endpoint='/script/http/header')
    _create_permission(name='启用请求头', method='PATCH', endpoint='/script/http/header/enable')
    _create_permission(name='禁用请求头', method='PATCH', endpoint='/script/http/header/disable')
    _create_permission(name='查询模板下的请求头', method='GET', endpoint='/script/http/headers/by/template')
    _create_permission(name='根据列表查询请求头', method='GET', endpoint='/script/http/headers')
    _create_permission(name='根据列表批量新增请求头', method='POST', endpoint='/script/http/headers')
    _create_permission(name='根据列表批量修改请求头', method='PUT', endpoint='/script/http/headers')
    _create_permission(name='根据列表批量删除请求头', method='DELETE', endpoint='/script/http/headers')
    _create_permission(name='复制请求头模板', method='POST', endpoint='/script/http/headers/template/duplicate')
    _create_permission(name='复制请求头模板至指定工作空间', method='POST', endpoint='/script/http/headers/template/copy/to/workspace')
    _create_permission(name='移动请求头模板至指定工作空间', method='PATCH', endpoint='/script/http/headers/template/move/to/workspace')

    # testplan
    _create_permission(name='分页查询测试计划列表', method='GET', endpoint='/script/testplan/list')
    _create_permission(name='查询测试计划详情', method='GET', endpoint='/script/testplan')
    _create_permission(name='创建测试计划', method='POST', endpoint='/script/testplan')
    _create_permission(name='修改测试计划', method='PUT', endpoint='/script/testplan')
    _create_permission(name='修改测试计划状态', method='PATCH', endpoint='/script/testplan/state')
    _create_permission(name='修改测试计划测试阶段', method='PATCH', endpoint='/script/testplan/testphase')
    _create_permission(name='查询所有测试计划执行记录', method='GET', endpoint='/script/testplan/execution/all')
    _create_permission(name='查询测试计划执行记录详情', method='GET', endpoint='/script/testplan/execution/details')

    # report
    _create_permission(name='查询测试报告', method='GET', endpoint='/script/report')
    _create_permission(
        name='根据 collectionId 查询 Collection 结果和 Group 结果列表',
        method='GET',
        endpoint='/script/report/collection/result'
    )
    _create_permission(name='根据 groupId 查询 GroupGroup 结果', method='GET', endpoint='/script/report/group/result')
    _create_permission(name='根据 samplerId 查询 Sampler 结果', method='GET', endpoint='/script/report/sampler/result')

    click.echo('创建权限成功')


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联"""
    user = TUser.filter_by(USER_NAME='超级管理员').first()
    role = TRole.filter_by(ROLE_NAME='SuperAdmin', ROLE_DESC='超级管理员').first()
    TUserRoleRel.insert(USER_NO=user.USER_NO, ROLE_NO=role.ROLE_NO)
    click.echo('创建用户角色关联成功')


@with_appcontext
def init_role_permission_rel():
    """初始化角色权限关联"""
    permissions = TPermission.query.all()
    role = TRole.filter_by(ROLE_NAME='SuperAdmin', ROLE_DESC='超级管理员').first()
    for permission in permissions:
        TRolePermissionRel.insert(ROLE_NO=role.ROLE_NO, PERMISSION_NO=permission.PERMISSION_NO)
    click.echo('创建角色权限关联成功')


@with_appcontext
def init_script_global_variable_set():
    TVariableDataset.insert(DATASET_NO=new_id(), DATASET_NAME='public', DATASET_TYPE='GLOBAL', WEIGHT=1)
    click.echo('初始化PyMeter全局变量成功')


@with_appcontext
def init_action_log():
    TActionLog.insert(ACTION_DESC='INIT DB')
    click.echo('初始化操作日志数据成功')


def _create_role(name, role_desc):
    TRole.insert(ROLE_NO=new_id(), ROLE_NAME=name, ROLE_DESC=role_desc, STATE='ENABLE')


def _create_permission(name, method, endpoint):
    TPermission.insert(PERMISSION_NO=new_id(), PERMISSION_NAME=name, METHOD=method, ENDPOINT=endpoint, STATE='ENABLE')


@click.command('sqlite-to-pgsql')
@with_appcontext
def migrate_sqlite_to_pgsql():
    import app
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.script import model

    sqlite_engine = create_engine(app.get_sqlite_url())
    sqlite_session = Session(sqlite_engine)

    # TWorkspaceCollectionRel
    for entity in sqlite_session.query(model.TWorkspaceCollectionRel).filter_by(DEL_STATE=0).all():
        model.TWorkspaceCollectionRel.insert(
            WORKSPACE_NO=entity.WORKSPACE_NO,
            COLLECTION_NO=entity.COLLECTION_NO
        )
        click.echo(f'success insert into TWorkspaceCollectionRel value {entity.WORKSPACE_NO} {entity.COLLECTION_NO}')

    # TTestElement
    for entity in sqlite_session.query(model.TTestElement).filter_by(DEL_STATE=0).all():
        model.TTestElement.insert(
            ELEMENT_NO=entity.ELEMENT_NO,
            ELEMENT_NAME=entity.ELEMENT_NAME,
            ELEMENT_REMARK=entity.ELEMENT_REMARK,
            ELEMENT_TYPE=entity.ELEMENT_TYPE,
            ELEMENT_CLASS=entity.ELEMENT_CLASS,
            ENABLED=entity.ENABLED,
            META_DATA=entity.META_DATA
        )
        click.echo(f'success insert into TTestElement value {entity.ELEMENT_NO}')

    # TElementProperty
    for entity in sqlite_session.query(model.TElementProperty).filter_by(DEL_STATE=0).all():
        model.TElementProperty.insert(
            ELEMENT_NO=entity.ELEMENT_NO,
            PROPERTY_NAME=entity.PROPERTY_NAME,
            PROPERTY_VALUE=(
                entity.PROPERTY_VALUE
                if not isinstance(entity.PROPERTY_VALUE, bytes)
                else str(entity.PROPERTY_VALUE, encoding='utf8')
            ),
            PROPERTY_TYPE=entity.PROPERTY_TYPE,
            ENABLED=entity.ENABLED
        )
        click.echo(f'success insert into TElementProperty value {entity.ELEMENT_NO}')

    # TElementChildRel
    for entity in sqlite_session.query(model.TElementChildRel).filter_by(DEL_STATE=0).all():
        model.TElementChildRel.insert(
            ROOT_NO=entity.ROOT_NO,
            PARENT_NO=entity.PARENT_NO,
            CHILD_NO=entity.CHILD_NO,
            SERIAL_NO=entity.SERIAL_NO
        )
        click.echo(f'success insert into TElementChildRel value {entity.PARENT_NO} {entity.CHILD_NO}')

    # TElementBuiltinChildRel
    for entity in sqlite_session.query(model.TElementBuiltinChildRel).filter_by(DEL_STATE=0).all():
        model.TElementBuiltinChildRel.insert(
            ROOT_NO=entity.ROOT_NO,
            PARENT_NO=entity.PARENT_NO,
            CHILD_NO=entity.CHILD_NO,
            CHILD_TYPE=entity.CHILD_TYPE
        )
        click.echo(f'success insert into TElementBuiltinChildRel value {entity.PARENT_NO} {entity.CHILD_NO}')

    # TVariableDataset
    for entity in sqlite_session.query(model.TVariableDataset).filter_by(DEL_STATE=0).all():
        model.TVariableDataset.insert(
            WORKSPACE_NO=entity.WORKSPACE_NO,
            DATASET_NO=entity.DATASET_NO,
            DATASET_NAME=entity.DATASET_NAME,
            DATASET_TYPE=entity.DATASET_TYPE,
            DATASET_DESC=entity.DATASET_DESC,
            WEIGHT=entity.WEIGHT
        )
        click.echo(f'success insert into TVariableDataset value {entity.DATASET_NO}')

    # TVariable
    for entity in sqlite_session.query(model.TVariable).filter_by(DEL_STATE=0).all():
        model.TVariable.insert(
            DATASET_NO=entity.DATASET_NO,
            VAR_NO=entity.VAR_NO,
            VAR_NAME=entity.VAR_NAME,
            VAR_DESC=entity.VAR_DESC,
            INITIAL_VALUE=entity.INITIAL_VALUE,
            CURRENT_VALUE=entity.CURRENT_VALUE,
            ENABLED=entity.ENABLED
        )
        click.echo(f'success insert into TVariable value {entity.VAR_NO}')

    # THttpSamplerHeadersRel
    for entity in sqlite_session.query(model.THttpSamplerHeadersRel).filter_by(DEL_STATE=0).all():
        model.THttpSamplerHeadersRel.insert(
            SAMPLER_NO=entity.SAMPLER_NO,
            TEMPLATE_NO=entity.TEMPLATE_NO
        )
        click.echo(f'success insert into THttpSamplerHeadersRel value {entity.SAMPLER_NO} {entity.TEMPLATE_NO}')

    # THttpHeadersTemplate
    for entity in sqlite_session.query(model.THttpHeadersTemplate).filter_by(DEL_STATE=0).all():
        model.THttpHeadersTemplate.insert(
            WORKSPACE_NO=entity.WORKSPACE_NO,
            TEMPLATE_NO=entity.TEMPLATE_NO,
            TEMPLATE_NAME=entity.TEMPLATE_NAME,
            TEMPLATE_DESC=entity.TEMPLATE_DESC
        )
        click.echo(f'success insert into THttpHeadersTemplate value {entity.TEMPLATE_NO}')

    # THttpHeader
    for entity in sqlite_session.query(model.THttpHeader).filter_by(DEL_STATE=0).all():
        model.THttpHeader.insert(
            TEMPLATE_NO=entity.TEMPLATE_NO,
            HEADER_NO=entity.HEADER_NO,
            HEADER_NAME=entity.HEADER_NAME,
            HEADER_VALUE=entity.HEADER_VALUE,
            HEADER_DESC=entity.HEADER_DESC,
            ENABLED=entity.ENABLED
        )
        click.echo(f'success insert into THttpHeader value {entity.HEADER_NO}')

    sqlite_session.close()
