#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : command.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from app.common.id_generator import new_id
from app.extension import db
from app.script.model import TVariableSet
from app.system.model import TActionLog
from app.system.model import TWorkspace
from app.system.model import TWorkspaceUserRel
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
        WORKSPACE_TYPE='PUBLIC',
        WORKSPACE_SCOPE='PERSONAL'
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
    _create_permission(name='分页查询用户角色关联关系列表', method='GET', endpoint='/user/role/rel/list')
    _create_permission(name='新增用户角色关联关系', method='POST', endpoint='/user/role/rel')
    _create_permission(name='删除用户角色关联关系', method='DELETE', endpoint='/user/role/rel')
    _create_permission(name='分页查询角色权限关联关系列表', method='GET', endpoint='/user/role/permission/rel/list')
    _create_permission(name='新增角色权限关联关系', method='POST', endpoint='/user/role/permission/rel')
    _create_permission(name='删除角色权限关联关系', method='DELETE', endpoint='/user/role/permission/rel')

    # system模块路由
    # log
    _create_permission(name='分页查询操作日志列表', method='GET', endpoint='/system/action/log/list')
    # workspace
    _create_permission(name='分页查询工作空间列表', method='GET', endpoint='/system/workspace/list')
    _create_permission(name='查询所有工作空间', method='GET', endpoint='/system/workspace/all')
    _create_permission(name='新增工作空间', method='POST', endpoint='/system/workspace')
    _create_permission(name='修改工作空间', method='PUT', endpoint='/system/workspace')
    _create_permission(name='删除工作空间', method='DELETE', endpoint='/system/workspace')
    _create_permission(name='添加工作空间成员', method='POST', endpoint='/system/workspace/user')
    _create_permission(name='修改工作空间成员', method='PUT', endpoint='/system/workspace/user')
    _create_permission(name='删除工作空间成员', method='DELETE', endpoint='/system/workspace/user')

    # script模块路由
    # element
    _create_permission(name='分页查询测试元素列表', method='GET', endpoint='/script/element/list')
    _create_permission(name='查询所有测试元素', method='GET', endpoint='/script/element/all')
    _create_permission(name='查询测试元素信息', method='GET', endpoint='/script/element/info')
    _create_permission(name='查询测试元素子代', method='GET', endpoint='/script/element/children')
    _create_permission(name='新增测试元素', method='POST', endpoint='/script/element')
    _create_permission(name='修改测试元素', method='PUT', endpoint='/script/element')
    _create_permission(name='删除测试元素', method='DELETE', endpoint='/script/element')
    _create_permission(name='启用元素', method='PATCH', endpoint='/script/element/enable')
    _create_permission(name='禁用元素', method='PATCH', endpoint='/script/element/disable')
    _create_permission(name='添加元素属性', method='POST', endpoint='/script/element/property')
    _create_permission(name='修改元素属性', method='PUT', endpoint='/script/element/property')
    _create_permission(name='根据父元素编号新增元素子代', method='POST', endpoint='/script/element/children')
    _create_permission(name='根据父元素编号修改元素子代', method='PUT', endpoint='/script/element/children')
    _create_permission(name='根据父元素编号和子元素编号上移序号', method='PATCH', endpoint='/script/element/child/order/up')
    _create_permission(name='根据父元素编号和子元素编号下移序号', method='PATCH', endpoint='/script/element/child/order/down')
    _create_permission(name='复制测试元素及其子代', method='POST', endpoint='/script/element/duplicate')

    # execution
    _create_permission(name='执行脚本', method='POST', endpoint='/script/execute')

    # variables
    _create_permission(name='分页查询变量集列表', method='GET', endpoint='/script/variable/set/list')
    _create_permission(name='查询所有变量集', method='GET', endpoint='/script/variable/set/all')
    _create_permission(name='查询变量集下的所有变量', method='GET', endpoint='/script/variable/set')
    _create_permission(name='新增变量集', method='POST', endpoint='/script/variable/set')
    _create_permission(name='修改变量集', method='PUT', endpoint='/script/variable/set')
    _create_permission(name='删除变量集', method='DELETE', endpoint='/script/variable/set')
    _create_permission(name='新增变量', method='POST', endpoint='/script/variable')
    _create_permission(name='修改变量', method='PUT', endpoint='/script/variable')
    _create_permission(name='删除变量', method='DELETE', endpoint='/script/variable')
    _create_permission(name='启用变量', method='PATCH', endpoint='/script/variable/enable')
    _create_permission(name='禁用变量', method='PATCH', endpoint='/script/variable/disable')
    _create_permission(name='更新变量当前值', method='PATCH', endpoint='/script/variable/current/value')
    _create_permission(name='根据变量集编号列表查询变量', method='GET', endpoint='/script/variables')
    _create_permission(name='根据列表批量新增变量', method='POST', endpoint='/script/variables')
    _create_permission(name='根据列表批量修改变量', method='PUT', endpoint='/script/variables')
    _create_permission(name='根据列表批量删除变量', method='DELETE', endpoint='/script/variables')

    click.echo('创建权限成功')


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联关系"""
    user = TUser.query.filter_by(USER_NAME='超级管理员').first()
    role = TRole.query.filter_by(ROLE_NAME='SuperAdmin', ROLE_DESC='超级管理员').first()
    TUserRoleRel.insert(USER_NO=user.USER_NO, ROLE_NO=role.ROLE_NO)
    click.echo('创建用户角色关联关系成功')


@with_appcontext
def init_role_permission_rel():
    """初始化角色权限关联关系"""
    permissions = TPermission.query.all()
    role = TRole.query.filter_by(ROLE_NAME='SuperAdmin', ROLE_DESC='超级管理员').first()
    for permission in permissions:
        TRolePermissionRel.insert(ROLE_NO=role.ROLE_NO, PERMISSION_NO=permission.PERMISSION_NO)
    click.echo('创建角色权限关联关系成功')


@with_appcontext
def init_script_global_variable_set():
    TVariableSet.insert(SET_NO=new_id(), SET_NAME='public', SET_TYPE='GLOBAL')
    click.echo('初始化PyMeter全局变量成功')


@with_appcontext
def init_action_log():
    TActionLog.insert(ACTION_DESC='INIT DB')
    click.echo('初始化操作日志数据成功')


def _create_role(name, role_desc):
    TRole.insert(ROLE_NO=new_id(), ROLE_NAME=name, ROLE_DESC=role_desc, STATE='ENABLE')


def _create_permission(name, method, endpoint):
    TPermission.insert(PERMISSION_NO=new_id(), PERMISSION_NAME=name, METHOD=method, ENDPOINT=endpoint, STATE='ENABLE')
