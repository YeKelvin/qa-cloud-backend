#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : commands.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
from datetime import datetime

import click
from flask.cli import with_appcontext

from server.common.number_generator import generate_user_no, generate_role_no, generate_permission_no
from server.extensions import db
from server.librarys.sequence import TSequence
from server.script.model import (
    TTestProject, TItemTopicRel, TItemCollectionRel, TItemUserRel, TTestTopic, TTopicCollectionRel, TTestElement,
    TElementProperty, TElementChildRel, TEnvironmentVariableCollection, TEnvironmentVariableCollectionRel,
    TEnvironmentVariable, THTTPHeaderCollection, THTTPHeaderCollectionRel, THTTPHeader, TSQLConfiguration,
    TElementPackage, TPackageElementRel, TScriptActivityLog
)
from server.system.model import TActionLog
from server.user.model import TUser, TRole, TPermission, TUserRoleRel, TRolePermissionRel, TUserLoginInfo, TUserPassword

from server.utils.log_util import get_logger

log = get_logger(__name__)


@click.command()
@click.option(
    '-d',
    '--drop',
    default=False,
    help='初始化数据库前是否先删除所有表，默认False'
)
@with_appcontext
def initdb(drop):
    """创建表
    """
    if drop:
        db.drop_all()
        click.echo('删除所有数据库表成功')
    db.create_all()
    click.echo('创建所有数据库表成功')


@click.command()
def initdata():
    """初始化数据
    """
    init_seq()
    init_user()
    init_role()
    init_permission()
    init_user_role_rel()
    init_role_permission_rel()
    init_action_log()
    click.echo('初始化数据成功')


@with_appcontext
def init_seq():
    """初始化序列（SQLite专用）
    """
    TSequence.create(SEQ_NAME='seq_user_no')
    TSequence.create(SEQ_NAME='seq_role_no')
    TSequence.create(SEQ_NAME='seq_permission_no')
    TSequence.create(SEQ_NAME='seq_item_no')
    TSequence.create(SEQ_NAME='seq_topic_no')
    TSequence.create(SEQ_NAME='seq_element_no')
    TSequence.create(SEQ_NAME='seq_http_header_no')
    TSequence.create(SEQ_NAME='seq_env_var_no')
    TSequence.create(SEQ_NAME='seq_package_no')
    click.echo('创建序列成功')


@with_appcontext
def init_user():
    """初始化用户
    """
    TUser.create(
        USER_NO=generate_user_no(),  # U0000000001
        USER_NAME='超级管理员',
        STATE='ENABLE'
    )

    TUserLoginInfo.create(
        USER_NO='U0000000001',
        LOGIN_NAME='admin',
        LOGIN_TYPE='MOBILE'
    )

    TUserPassword.create(
        PASSWORD=TUserPassword.generate_password_hash('admin', 'admin'),
        PASSWORD_TYPE='LOGIN',
        ERROR_TIMES=0,
        CREATE_TYPE='CUSTOMER'
    )
    click.echo('创建 admin用户成功')


@with_appcontext
def init_role():
    """初始化角色
    """
    __create_role(name='SuperAdmin', role_desc='超级管理员')  # R0000000001
    __create_role(name='Admin', role_desc='管理员')  # R0000000002
    __create_role(name='Leader', role_desc='组长')  # R0000000003
    __create_role(name='General', role_desc='用户')  # R0000000004

    click.echo('创建角色成功')


@with_appcontext
def init_permission():
    """初始化权限
    """
    # user模块路由
    __create_permission(name='用户登录', method='POST', endpoint='/user/login')
    __create_permission(name='用户登出', method='POST', endpoint='/user/logout')
    __create_permission(name='用户注册', method='POST', endpoint='/user/register')
    __create_permission(name='重置密码', method='PATCH', endpoint='/user/password/reset')
    __create_permission(name='查询用户信息', method='GET', endpoint='/user/info')
    __create_permission(name='分页查询用户列表', method='GET', endpoint='/user/list')
    __create_permission(name='查询所有用户', method='GET', endpoint='/user/all')
    __create_permission(name='更新用户信息', method='PUT', endpoint='/user/info')
    __create_permission(name='更新用户状态', method='PATCH', endpoint='/user/info/state')
    __create_permission(name='删除用户', method='DELETE', endpoint='/user')
    __create_permission(name='分页查询权限列表', method='GET', endpoint='/user/permission/list')
    __create_permission(name='查询所有权限', method='GET', endpoint='/user/permission/all')
    __create_permission(name='新增权限', method='POST', endpoint='/user/permission')
    __create_permission(name='更新权限信息', method='PUT', endpoint='/user/permission')
    __create_permission(name='更新权限状态', method='PATCH', endpoint='/user/permission/state')
    __create_permission(name='删除权限', method='DELETE', endpoint='/user/permission')
    __create_permission(name='分页查询角色列表', method='GET', endpoint='/user/role/list')
    __create_permission(name='查询所有角色', method='GET', endpoint='/user/role/all')
    __create_permission(name='新增角色', method='POST', endpoint='/user/role')
    __create_permission(name='更新角色信息', method='PUT', endpoint='/user/role')
    __create_permission(name='更新角色状态', method='PATCH', endpoint='/user/role/state')
    __create_permission(name='删除角色', method='DELETE', endpoint='/user/role')
    __create_permission(name='分页查询用户角色关联关系列表', method='GET', endpoint='/user/role/rel/list')
    __create_permission(name='新增用户角色关联关系', method='POST', endpoint='/user/role/rel')
    __create_permission(name='删除用户角色关联关系', method='DELETE', endpoint='/user/role/rel')
    __create_permission(name='分页查询角色权限关联关系列表', method='GET', endpoint='/user/role/permission/rel/list')
    __create_permission(name='新增角色权限关联关系', method='POST', endpoint='/user/role/permission/rel')
    __create_permission(name='删除角色权限关联关系', method='DELETE', endpoint='/user/role/permission/rel')

    # system模块路由
    __create_permission(name='分页查询操作日志列表', method='GET', endpoint='/system/action/log/list')

    # script模块路由
    # item
    __create_permission(name='分页查询测试项目列表', method='GET', endpoint='/script/item/list')
    __create_permission(name='查询所有测试项目', method='GET', endpoint='/script/item/all')
    __create_permission(name='新增测试项目', method='POST', endpoint='/script/item')
    __create_permission(name='修改测试项目', method='PUT', endpoint='/script/item')
    __create_permission(name='删除测试项目', method='DELETE', endpoint='/script/item')
    __create_permission(name='添加测试项目成员', method='POST', endpoint='/script/item/user')
    __create_permission(name='修改测试项目成员', method='PUT', endpoint='/script/item/user')
    __create_permission(name='删除测试项目成员', method='DELETE', endpoint='/script/item/user')

    # topic
    __create_permission(name='分页查询测试主题列表', method='GET', endpoint='/script/topic/list')
    __create_permission(name='查询所有测试主题', method='GET', endpoint='/script/topic/all')
    __create_permission(name='新增测试主题', method='POST', endpoint='/script/topic')
    __create_permission(name='修改测试主题', method='PUT', endpoint='/script/topic')
    __create_permission(name='删除测试主题', method='DELETE', endpoint='/script/topic')
    __create_permission(name='添加测试主题下的集合', method='POST', endpoint='/script/topic/collection')
    __create_permission(name='修改测试主题下的集合', method='PUT', endpoint='/script/topic/collection')
    __create_permission(name='删除测试主题下的集合', method='DELETE', endpoint='/script/topic/collection')

    # element
    __create_permission(name='分页查询测试元素列表', method='GET', endpoint='/script/element/list')
    __create_permission(name='查询所有测试元素', method='GET', endpoint='/script/element/all')
    __create_permission(name='查询测试元素信息', method='GET', endpoint='/script/element/info')
    __create_permission(name='查询测试元素子代', method='GET', endpoint='/script/element/child')
    __create_permission(name='新增测试元素', method='POST', endpoint='/script/element')
    __create_permission(name='修改测试元素', method='PUT', endpoint='/script/element')
    __create_permission(name='删除测试元素', method='DELETE', endpoint='/script/element')
    __create_permission(name='启用元素', method='PATCH', endpoint='/script/element/enable')
    __create_permission(name='禁用元素', method='PATCH', endpoint='/script/element/disable')
    __create_permission(name='添加元素属性', method='POST', endpoint='/script/element/property')
    __create_permission(name='修改元素属性', method='PUT', endpoint='/script/element/property')
    __create_permission(name='根据父元素编号新增元素子代', method='POST', endpoint='/script/element/child')
    __create_permission(name='根据父元素编号修改元素子代', method='PUT', endpoint='/script/element/child')
    __create_permission(name='根据父元素编号和子元素编号上移序号', method='PATCH', endpoint='/script/element/child/order/up')
    __create_permission(name='根据父元素编号和子元素编号下移序号', method='PATCH', endpoint='/script/element/child/order/down')
    __create_permission(name='复制测试元素及其子代', method='POST', endpoint='/script/element/duplicate')

    # environment variable

    click.echo('创建权限成功')


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联关系
    """
    TUserRoleRel.create(USER_NO='U0000000001', ROLE_NO='R0000000001')
    click.echo('创建用户角色关联关系成功')


@with_appcontext
def init_role_permission_rel():
    """初始化角色权限关联关系
    """
    permissions = TPermission.query.all()
    for permission in permissions:
        TRolePermissionRel.create(ROLE_NO='R0000000001', PERMISSION_NO=permission.permission_no)
    click.echo('创建角色权限关联关系成功')


@with_appcontext
def init_action_log():
    TActionLog.create(ACTION_DESC='init database data')
    click.echo('初始化操作日志数据成功')


def __create_role(name, role_desc):
    TRole.create(ROLE_NO=generate_role_no(), ROLE_NAME=name, ROLE_DESC=role_desc, STATE='ENABLE')


def __create_permission(name, method, endpoint):
    TPermission.create(PERMISSION_NO=generate_permission_no(), PERMISSION_NAME=name,
                       METHOD=method, ENDPOINT=endpoint, STATE='ENABLE')
