#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : commands.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
from datetime import datetime

import click
from flask.cli import with_appcontext

from server.extensions import db
from server.librarys.sequence import TSequence
from server.script.model import (
    TTestItem, TItemTopicRel, TItemUserRel, TTestTopic, TTopicCollectionRel, TTestElement,
    TElementChildRel, TEnvironmentVariableCollection, TEnvironmentVariableCollectionRel, TEnvironmentVariable,
    THTTPHeaderCollection, THTTPHeaderCollectionRel, THTTPHeader, TSQLConfiguration, TElementPackage,
    TPackageElementRel, TScriptActivityLog
)
from server.system.model import TActionLog
from server.user.model import TUser, TRole, TPermission, TUserRoleRel, TRolePermissionRel
from server.user.services.permission_service import generate_permission_no
from server.user.services.role_service import generate_role_no
from server.user.services.user_service import generate_user_no
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
    admin = TUser()
    admin.user_no = generate_user_no()  # U0000000001
    admin.username = 'admin'
    admin.nickname = '超级管理员'
    admin.password = 'admin'
    admin.state = 'NORMAL'
    admin.created_time = datetime.now()
    admin.created_by = 'system'
    admin.save()
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
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登录',
                       method='POST', endpoint='/user/login',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登出',
                       method='POST', endpoint='/user/logout',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户注册',
                       method='POST', endpoint='/user/register',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='重置密码',
                       method='PATCH', endpoint='/user/password/reset',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询用户信息',
                       method='GET', endpoint='/user/info',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询用户列表',
                       method='GET', endpoint='/user/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有用户',
                       method='GET', endpoint='/user/all',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新用户信息',
                       method='PUT', endpoint='/user/info',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新用户状态',
                       method='PATCH', endpoint='/user/info/state',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除用户',
                       method='DELETE', endpoint='/user',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询权限列表',
                       method='GET', endpoint='/user/permission/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有权限',
                       method='GET', endpoint='/user/permission/all',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增权限',
                       method='POST', endpoint='/user/permission',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新权限信息',
                       method='PUT', endpoint='/user/permission',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新权限状态',
                       method='PATCH', endpoint='/user/permission/state',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除权限',
                       method='DELETE', endpoint='/user/permission',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询角色列表',
                       method='GET', endpoint='/user/role/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有角色',
                       method='GET', endpoint='/user/role/all',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增角色',
                       method='POST', endpoint='/user/role',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新角色信息',
                       method='PUT', endpoint='/user/role',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新角色状态',
                       method='PATCH', endpoint='/user/role/state',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除角色',
                       method='DELETE', endpoint='/user/role',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询用户角色关联关系列表',
                       method='GET', endpoint='/user/role/rel/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增用户角色关联关系',
                       method='POST', endpoint='/user/role/rel',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除用户角色关联关系',
                       method='DELETE', endpoint='/user/role/rel',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询角色权限关联关系列表',
                       method='GET', endpoint='/user/role/permission/rel/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增角色权限关联关系',
                       method='POST', endpoint='/user/role/permission/rel',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除角色权限关联关系',
                       method='DELETE', endpoint='/user/role/permission/rel',
                       state='NORMAL', created_time=datetime.now(), created_by='system')

    # system模块路由
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询操作日志列表',
                       method='GET', endpoint='/system/action/log/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')

    # script模块路由
    # item
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询测试项目列表',
                       method='GET', endpoint='/script/item/list',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有测试项目',
                       method='GET', endpoint='/script/item/all',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增测试项目',
                       method='POST', endpoint='/script/item',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='修改测试项目',
                       method='PUT', endpoint='/script/item',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除测试项目',
                       method='DELETE', endpoint='/script/item',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='添加测试项目成员',
                       method='POST', endpoint='/script/item/user',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='修改测试项目成员',
                       method='PUT', endpoint='/script/item/user',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除测试项目成员',
                       method='DELETE', endpoint='/script/item/user',
                       state='NORMAL', created_time=datetime.now(), created_by='system')
    # topic

    # element

    # environment variable

    click.echo('创建权限成功')


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联关系
    """
    TUserRoleRel.create(user_no='U0000000001', role_no='R0000000001', created_time=datetime.now(), created_by='system')
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
        action_detail='init',
        action_path=None,
        created_time=datetime.now(),
        created_by='system',
    )
    click.echo('初始化操作日志数据成功')
