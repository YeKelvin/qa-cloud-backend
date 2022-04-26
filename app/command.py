#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : command.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from app.common.id_generator import new_id
from app.extension import db  # noqa
from app.database import TSystemOperationLogContent  # noqa
from app.public.model import TWorkspace  # noqa
from app.public.model import TWorkspaceUser  # noqa
from app.script.model import TVariableDataset  # noqa
from app.usercenter.model import TPermission  # noqa
from app.usercenter.model import TRole  # noqa
from app.usercenter.model import TRolePermission  # noqa
from app.usercenter.model import TUser  # noqa
from app.usercenter.model import TUserLoginInfo  # noqa
from app.usercenter.model import TUserPassword  # noqa
from app.usercenter.model import TUserRole  # noqa
from app.utils.log_util import get_logger  # noqa
from app.utils.security import encrypt_password


from app.script.model import *  # noqa isort:skip
from app.system.model import *  # noqa isort:skip
from app.public.model import *  # noqa isort:skip
from app.usercenter.model import *  # noqa isort:skip


log = get_logger(__name__)


@click.command()
@with_appcontext
def initdb():
    """创建表"""
    db.create_all()
    click.echo('创建所有数据库表成功')


@click.command()
@click.option('-m', '--confirm', help='删除所有表，删除前需要输入确认信息，注意：该命令仅用于开发环境！！！')
@with_appcontext
def dropdb(confirm):
    if not confirm:
        click.echo('请输入删除表格的确认信息')
        return
    if confirm != 'only use on development!!!':
        click.echo('确认信息不正确，请重试')
        return
    db.drop_all()
    click.echo('删除所有数据库表成功')


@click.command()
def initdata():
    """初始化数据"""
    init_user()
    init_role()
    init_permission()
    init_user_role()
    init_global_variable_dataset()
    click.echo('初始化数据成功')


@with_appcontext
def init_user():
    """初始化用户"""
    user_no = new_id()
    TUser.insert(USER_NO=user_no, USER_NAME='超级管理员')
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
    TWorkspaceUser.insert(WORKSPACE_NO=worksapce_no, USER_NO=user_no)

    click.echo('创建 admin用户成功')


@with_appcontext
def init_role():
    """初始化角色"""
    _create_role(name='超级管理员', code='SUPER_ADMIN', rank='9999')
    _create_role(name='管理员', code='ADMIN', rank='9000')
    _create_role(name='组长', code='LEADER', rank='1000')
    _create_role(name='用户', code='GENERAL', rank='1')

    click.echo('创建角色成功')


@with_appcontext
def init_permission():
    """初始化权限"""
    # usercenter模块路由
    # user
    _create_permission(name='用户登录', method='POST', endpoint='/usercenter/user/login')
    _create_permission(name='用户登出', method='POST', endpoint='/usercenter/user/logout')
    _create_permission(name='用户注册', method='POST', endpoint='/usercenter/user/register')
    _create_permission(name='重置密码', method='PATCH', endpoint='/usercenter/user/password/reset')
    _create_permission(name='查询用户信息', method='GET', endpoint='/usercenter/user/info')
    _create_permission(name='分页查询用户列表', method='GET', endpoint='/usercenter/user/list')
    _create_permission(name='查询所有用户', method='GET', endpoint='/usercenter/user/all')
    _create_permission(name='更新用户信息', method='PUT', endpoint='/usercenter/user/info')
    _create_permission(name='更新用户状态', method='PATCH', endpoint='/usercenter/user/state')
    _create_permission(name='删除用户', method='DELETE', endpoint='/usercenter/user')
    # permission
    _create_permission(name='分页查询权限列表', method='GET', endpoint='/usercenter/permission/list')
    _create_permission(name='查询所有权限', method='GET', endpoint='/usercenter/permission/all')
    _create_permission(name='新增权限', method='POST', endpoint='/usercenter/permission')
    _create_permission(name='更新权限信息', method='PUT', endpoint='/usercenter/permission')
    _create_permission(name='更新权限状态', method='PATCH', endpoint='/usercenter/permission/state')
    _create_permission(name='删除权限', method='DELETE', endpoint='/usercenter/permission')
    # role
    _create_permission(name='分页查询角色列表', method='GET', endpoint='/usercenter/role/list')
    _create_permission(name='查询所有角色', method='GET', endpoint='/usercenter/role/all')
    _create_permission(name='查询角色信息', method='GET', endpoint='/usercenter/role/info')
    _create_permission(name='新增角色', method='POST', endpoint='/usercenter/role')
    _create_permission(name='更新角色信息', method='PUT', endpoint='/usercenter/role')
    _create_permission(name='更新角色状态', method='PATCH', endpoint='/usercenter/role/state')
    _create_permission(name='删除角色', method='DELETE', endpoint='/usercenter/role')
    _create_permission(name='分页查询用户角色列表', method='GET', endpoint='/usercenter/user/role/list')
    _create_permission(name='查询所有用户角色', method='GET', endpoint='/usercenter/user/role/all')
    _create_permission(name='分页查询角色权限列表', method='GET', endpoint='/usercenter/role/permission/list')
    _create_permission(name='分页查询角色未绑定的权限列表', method='GET', endpoint='/usercenter/role/permission/unbound/list')
    _create_permission(name='批量新增角色权限', method='POST', endpoint='/usercenter/role/permissions')
    _create_permission(name='删除角色权限', method='DELETE', endpoint='/usercenter/role/permission')
    _create_permission(name='批量删除角色权限', method='DELETE', endpoint='/usercenter/role/permissions')
    # group
    _create_permission(name='分页查询分组列表', method='GET', endpoint='/usercenter/group/list')
    _create_permission(name='查询所有分组', method='GET', endpoint='/usercenter/group/all')
    _create_permission(name='查询分组信息', method='GET', endpoint='/usercenter/group/info')
    _create_permission(name='新增分组', method='POST', endpoint='/usercenter/group')
    _create_permission(name='更新分组信息', method='PUT', endpoint='/usercenter/group')
    _create_permission(name='更新分组状态', method='PATCH', endpoint='/usercenter/group/state')
    _create_permission(name='删除分组', method='DELETE', endpoint='/usercenter/group')

    # system模块路由
    # log
    _create_permission(name='分页查询操作日志列表', method='GET', endpoint='/system/operation/log/list')

    # public模块路由
    # workspace
    _create_permission(name='分页查询工作空间列表', method='GET', endpoint='/public/workspace/list')
    _create_permission(name='查询所有工作空间', method='GET', endpoint='/public/workspace/all')
    _create_permission(name='查询工作空间信息', method='GET', endpoint='/public/workspace/info')
    _create_permission(name='新增工作空间', method='POST', endpoint='/public/workspace')
    _create_permission(name='修改工作空间', method='PUT', endpoint='/public/workspace')
    _create_permission(name='删除工作空间', method='DELETE', endpoint='/public/workspace')
    _create_permission(name='分页查询空间成员列表', method='GET', endpoint='/public/workspace/user/list')
    _create_permission(name='查询所有空间成员', method='GET', endpoint='/public/workspace/user/all')
    _create_permission(name='修改空间成员', method='PUT', endpoint='/public/workspace/user')
    _create_permission(name='分页查询空间限制', method='GET', endpoint='/public/workspace/restriction/list')
    _create_permission(name='查询所有空间限制', method='GET', endpoint='/public/workspace/restriction/all')
    _create_permission(name='新增空间限制', method='POST', endpoint='/public/workspace/restriction')
    _create_permission(name='修改空间限制', method='PUT', endpoint='/public/workspace/restriction')
    _create_permission(name='删除空间限制', method='DELETE', endpoint='/public/workspace/restriction')
    _create_permission(name='启用空间限制', method='PATCH', endpoint='/public/workspace/restriction/enable')
    _create_permission(name='禁用空间限制', method='PATCH', endpoint='/public/workspace/restriction/disable')

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
    _create_permission(name='新增集合元素', method='POST', endpoint='/script/collection')
    _create_permission(name='根据父元素编号新增子代元素', method='POST', endpoint='/script/element/children')
    _create_permission(name='修改元素', method='PUT', endpoint='/script/element')
    _create_permission(name='修改多个元素（包含内置元素）', method='PUT', endpoint='/script/elements')
    _create_permission(name='删除元素', method='DELETE', endpoint='/script/element')
    _create_permission(name='启用元素', method='PATCH', endpoint='/script/element/enable')
    _create_permission(name='禁用元素', method='PATCH', endpoint='/script/element/disable')
    _create_permission(name='移动元素', method='POST', endpoint='/script/element/move')
    _create_permission(name='复制元素及其子代', method='POST', endpoint='/script/element/duplicate')
    _create_permission(name='查询HTTP请求头模板列表', method='GET', endpoint='/script/element/http/header/template/refs')
    _create_permission(name='新增HTTP请求头模板列表', method='POST', endpoint='/script/element/http/header/template/refs')
    _create_permission(name='修改HTTP请求头模板列表', method='PUT', endpoint='/script/element/http/header/template/refs')
    _create_permission(name='查询内置元素', method='GET', endpoint='/script/element/builtins')
    _create_permission(name='新增内置元素', method='POST', endpoint='/script/element/builtins')
    _create_permission(name='修改内置元素', method='PUT', endpoint='/script/element/builtins')
    _create_permission(name='剪贴元素', method='POST', endpoint='/script/element/paste')
    _create_permission(name='复制集合到指定空间', method='POST', endpoint='/script/element/collection/copy/to/workspace')
    _create_permission(name='移动集合到指定空间', method='POST', endpoint='/script/element/collection/move/to/workspace')

    # execution
    _create_permission(name='运行测试集合', method='POST', endpoint='/script/collection/execute')
    _create_permission(name='运行测试分组', method='POST', endpoint='/script/group/execute')
    _create_permission(name='运行请求取样器', method='POST', endpoint='/script/sampler/execute')
    _create_permission(name='运行片段集合', method='POST', endpoint='/script/snippets/execute')
    _create_permission(name='运行测试计划', method='POST', endpoint='/script/testplan/execute')
    _create_permission(name='中断运行测试计划', method='POST', endpoint='/script/testplan/execution/interrupt')
    _create_permission(name='查询测试集合的脚本（json）', method='GET', endpoint='/script/collection/json')
    _create_permission(name='查询测试分组的脚本（json）', method='GET', endpoint='/script/group/json')
    _create_permission(name='查询片段集合的脚本（json）', method='GET', endpoint='/script/snippets/json')

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
    _create_permission(name='移动变量集至指定工作空间', method='POST', endpoint='/script/variable/dataset/move/to/workspace')

    # headers
    _create_permission(name='分页查询请求头模板列表', method='GET', endpoint='/script/http/header/template/list')
    _create_permission(name='查询所有请求头模板', method='GET', endpoint='/script/http/header/template/all')
    _create_permission(name='新增请求头模板', method='POST', endpoint='/script/http/header/template')
    _create_permission(name='修改请求头模板', method='PUT', endpoint='/script/http/header/template')
    _create_permission(name='删除请求头模板', method='DELETE', endpoint='/script/http/header/template')
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
    _create_permission(name='复制请求头模板', method='POST', endpoint='/script/http/header/template/duplicate')
    _create_permission(name='复制请求头模板至指定工作空间', method='POST', endpoint='/script/http/header/template/copy/to/workspace')
    _create_permission(name='移动请求头模板至指定工作空间', method='POST', endpoint='/script/http/header/template/move/to/workspace')

    # database
    _create_permission(name='分页查询数据库引擎列表', method='GET', endpoint='/script/database/engine/list')
    _create_permission(name='查询所有数据库引擎', method='GET', endpoint='/script/database/engine/all')
    _create_permission(name='查询数据库引擎', method='GET', endpoint='/script/database/engine')
    _create_permission(name='新增数据库引擎', method='POST', endpoint='/script/database/engine')
    _create_permission(name='修改数据库引擎', method='PUT', endpoint='/script/database/engine')
    _create_permission(name='删除数据库引擎', method='DELETE', endpoint='/script/database/engine')
    _create_permission(name='复制数据库引擎', method='POST', endpoint='/script/database/engine/duplicate')
    _create_permission(name='复制数据库引擎至指定工作空间', method='POST', endpoint='/script/database/engine/copy/to/workspace')
    _create_permission(name='移动数据库引擎至指定工作空间', method='POST', endpoint='/script/database/engine/move/to/workspace')

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
def init_user_role():
    """初始化用户角色关联"""
    user = TUser.filter_by(USER_NAME='超级管理员').first()
    role = TRole.filter_by(ROLE_NAME='超级管理员', ROLE_CODE='SUPER_ADMIN').first()
    TUserRole.insert(USER_NO=user.USER_NO, ROLE_NO=role.ROLE_NO)
    click.echo('创建用户角色关联成功')


@with_appcontext
def init_global_variable_dataset():
    TVariableDataset.insert(DATASET_NO=new_id(), DATASET_NAME='public', DATASET_TYPE='GLOBAL', WEIGHT=1)
    click.echo('初始化PyMeter全局变量成功')


def _create_role(name, code, rank, desc=''):
    TRole.insert(ROLE_NO=new_id(), ROLE_NAME=name, ROLE_CODE=code, ROLE_RANK=rank, ROLE_DESC=desc)


def _create_permission(name, method, endpoint):
    TPermission.insert(PERMISSION_NO=new_id(), PERMISSION_NAME=name, METHOD=method, ENDPOINT=endpoint)


@click.command('create-table')
@click.option('-n', '--name', help='表名')
@with_appcontext
def create_single_table(name):
    from sqlalchemy import create_engine
    from app import get_db_url
    from app.script import model as script_model
    from app.system import model as system_model
    from app.public import model as public_model
    from app.usercenter import model as usercenter_model

    engine = create_engine(get_db_url())

    if hasattr(script_model, name):
        table = getattr(script_model, name)
    elif hasattr(system_model, name):
        table = getattr(system_model, name)
    elif hasattr(public_model, name):
        table = getattr(public_model, name)
    elif hasattr(usercenter_model, name):
        table = getattr(usercenter_model, name)
    else:
        table = None

    if table:
        table.__table__.create(engine, checkfirst=True)
        click.echo('新增表格成功')
    else:
        click.echo('表格名称不存在')
        return
