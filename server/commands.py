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
    TTestItem, TItemTopicRel, TItemUserRel, TTestTopic, TTopicCollectionRel, TTestElement, TElementProperty,
    TElementChildRel, TEnvironmentVariableCollection, TEnvironmentVariableCollectionRel, TEnvironmentVariable,
    THTTPHeaderCollection, THTTPHeaderCollectionRel, THTTPHeader, TSQLConfiguration, TElementPackage,
    TPackageElementRel, TScriptActivityLog
)
from server.system.model import TActionLog
from server.user.model import TUser, TRole, TPermission, TUserRoleRel, TRolePermissionRel

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
    TSequence.create(seq_name='seq_user_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_role_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_permission_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_item_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_topic_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_element_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_http_header_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_env_var_no', created_time=datetime.now(), created_by='system')
    TSequence.create(seq_name='seq_package_no', created_time=datetime.now(), created_by='system')
    click.echo('创建序列成功')


@with_appcontext
def init_user():
    """初始化用户
    """
    TUser.create(
        user_no=generate_user_no(),  # U0000000001
        username='admin',
        nickname='超级管理员',
        password='admin',
        state='NORMAL',
        created_time=datetime.now(),
        created_by='system'
    )
    click.echo('创建 admin用户成功')


@with_appcontext
def init_role():
    """初始化角色
    """
    TRole.create(role_no=generate_role_no(), role_name='SuperAdmin', state='NORMAL', description='超级管理员',
                 created_time=datetime.now(), created_by='system')  # R0000000001
    TRole.create(role_no=generate_role_no(), role_name='Admin', state='NORMAL', description='管理员',
                 created_time=datetime.now(), created_by='system')  # R0000000002
    TRole.create(role_no=generate_role_no(), role_name='Leader', state='NORMAL', description='组长',
                 created_time=datetime.now(), created_by='system')  # R0000000003
    TRole.create(role_no=generate_role_no(), role_name='General', state='NORMAL', description='用户',
                 created_time=datetime.now(), created_by='system')  # R0000000004
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

    # environment variable

    click.echo('创建权限成功')


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联关系
    """
    TUserRoleRel.create(
        user_no='U0000000001',
        role_no='R0000000001',
        created_time=datetime.now(),
        created_by='system'
    )
    click.echo('创建用户角色关联关系成功')


@with_appcontext
def init_role_permission_rel():
    """初始化角色权限关联关系
    """
    permissions = TPermission.query.all()
    for permission in permissions:
        TRolePermissionRel.create(role_no='R0000000001', permission_no=permission.permission_no,
                                  created_time=datetime.now(), created_by='system')
    click.echo('创建角色权限关联关系成功')


@with_appcontext
def init_action_log():
    TActionLog.create(
        action_detail='init database data',
        created_time=datetime.now(),
        created_by='system',
    )
    click.echo('初始化操作日志数据成功')


@click.command('add-permission')
@click.option('-n', '--name', help='权限名称')
@click.option('-m', '--method', help='请求方法')
@click.option('-e', '--endpoint', help='请求路由')
@with_appcontext
def add_permission(name, method, endpoint):
    """
    flask cli中添加权限
    
    e.g. flask add-permission -n name -m method -e endpoint
    """
    __create_permission(name, method, endpoint)
    click.echo(f'添加权限成功，name={name}，method={method}，endpoint={endpoint}')


def __create_permission(name, method, endpoint):
    TPermission.create(permission_no=generate_permission_no(), permission_name=name,
                       method=method, endpoint=endpoint,
                       state='NORMAL', created_time=datetime.now(), created_by='system')
