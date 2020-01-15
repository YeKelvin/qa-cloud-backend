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
from server.system.model import TActionLog
from server.user.model import TUser, TRole, TPermission, TUserRoleRel, TRolePermissionRel
from server.user.service import generate_user_no, generate_role_no, generate_permission_no
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
    click.echo('创建序列成功')


@with_appcontext
def init_user():
    """初始化用户
    """
    admin = TUser()
    admin.user_no = generate_user_no()  # U00000001
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
    TRole.create(role_no=generate_role_no(), role_name='SuperAdmin', state='NORMAL', remark='超级管理员',
                 created_time=datetime.now(), created_by='system')  # R00000001
    TRole.create(role_no=generate_role_no(), role_name='Admin', state='NORMAL', remark='管理员',
                 created_time=datetime.now(), created_by='system')  # R00000002
    TRole.create(role_no=generate_role_no(), role_name='Leader', state='NORMAL', remark='组长',
                 created_time=datetime.now(), created_by='system')  # R00000003
    TRole.create(role_no=generate_role_no(), role_name='General', state='NORMAL', remark='用户',
                 created_time=datetime.now(), created_by='system')  # R00000004
    click.echo('创建角色成功')


@with_appcontext
def init_permission():
    """初始化权限
    """
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登录', endpoint='/user/login',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登出', endpoint='/user/logout',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户注册', endpoint='/user/register',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='重置密码', endpoint='/user/password/reset',
                       method='PATCH', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询用户信息', endpoint='/user/info',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询用户列表', endpoint='/user/list',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有用户', endpoint='/user/all',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新用户信息', endpoint='/user/info',
                       method='PUT', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新用户状态', endpoint='/user/info/state',
                       method='PATCH', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除用户', endpoint='/user',
                       method='DELETE', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询权限列表',
                       endpoint='/user/permission/list',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有权限',
                       endpoint='/user/permission/all',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增权限', endpoint='/user/permission',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新权限信息', endpoint='/user/permission',
                       method='PUT', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新权限状态',
                       endpoint='/user/permission/state',
                       method='PATCH', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除权限', endpoint='/user/permission',
                       method='DELETE', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询角色列表',
                       endpoint='/user/role/list',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='查询所有角色',
                       endpoint='/user/role/all',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增角色', endpoint='/user/role',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新角色信息', endpoint='/user/role',
                       method='PUT', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='更新角色状态', endpoint='/user/role/state',
                       method='PATCH', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除角色', endpoint='/user/role',
                       method='DELETE', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询用户角色关联关系列表',
                       endpoint='/user/role/rel/list',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增用户角色关联关系',
                       endpoint='/user/role/rel',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除用户角色关联关系',
                       endpoint='/user/role/rel',
                       method='DELETE', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询角色权限关联关系列表',
                       endpoint='/user/role/permission/rel/list',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='新增角色权限关联关系',
                       endpoint='/user/role/permission/rel',
                       method='POST', state='NORMAL', created_time=datetime.now(), created_by='system')
    TPermission.create(permission_no=generate_permission_no(), permission_name='删除角色权限关联关系',
                       endpoint='/user/role/permission/rel',
                       method='DELETE', state='NORMAL', created_time=datetime.now(), created_by='system')

    TPermission.create(permission_no=generate_permission_no(), permission_name='分页查询操作日志列表',
                       endpoint='/system/action/log/list',
                       method='GET', state='NORMAL', created_time=datetime.now(), created_by='system')
    click.echo('创建权限成功')


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联关系
    """
    TUserRoleRel.create(user_no='U00000001', role_no='R00000001', created_time=datetime.now(), created_by='system')
    click.echo('创建用户角色关联关系成功')


@with_appcontext
def init_role_permission_rel():
    """初始化角色权限关联关系
    """
    permissions = TPermission.query.all()
    for permission in permissions:
        TRolePermissionRel.create(role_no='R00000001', permission_no=permission.permission_no,
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
