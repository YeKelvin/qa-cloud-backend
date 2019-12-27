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
from server.user.model import TUser, TRole, TPermission, TUserRoleRel, TRolePermissionRel, TMenu, TRoleMenuRel
from server.user.service import generate_user_no, generate_role_no, generate_permission_no, generate_menu_no
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
    init_menu()
    init_role_menu_rel()
    init_action_log()
    click.echo('初始化数据成功')


@with_appcontext
def init_seq():
    """初始化序列（SQLite专用）
    """
    TSequence.create(seq_name='seq_user_no', created_time=datetime.now(), created_by='system')
    click.echo('创建序列 seq_user_no成功')
    TSequence.create(seq_name='seq_role_no', created_time=datetime.now(), created_by='system')
    click.echo('创建序列 seq_role_no成功')
    TSequence.create(seq_name='seq_permission_no', created_time=datetime.now(), created_by='system')
    click.echo('创建序列 seq_permission_no成功')
    TSequence.create(seq_name='seq_menu_no', created_time=datetime.now(), created_by='system')
    click.echo('创建序列 seq_menu_no成功')


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
    TRole.create(role_no=generate_role_no(), role_name='超级管理员', created_time=datetime.now(),
                 created_by='system')  # R00000001
    TRole.create(role_no=generate_role_no(), role_name='系统管理员', created_time=datetime.now(),
                 created_by='system')  # R00000002
    TRole.create(role_no=generate_role_no(), role_name='管理员', created_time=datetime.now(),
                 created_by='system')  # R00000003
    TRole.create(role_no=generate_role_no(), role_name='帅哥美女', created_time=datetime.now(),
                 created_by='system')  # R00000004
    click.echo('创建角色成功')


@with_appcontext
def init_permission():
    """初始化权限
    """
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户注册', endpoint='/user/register',
                       method='POST', created_time=datetime.now(), created_by='system')  # P00000001
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登录', endpoint='/user/login',
                       method='POST', created_time=datetime.now(), created_by='system')  # P00000002
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登出', endpoint='/user/logout',
                       method='POST', created_time=datetime.now(), created_by='system')  # P00000003
    TPermission.create(permission_no=generate_permission_no(), permission_name='获取用户信息', endpoint='/user/info',
                       method='GET', created_time=datetime.now(), created_by='system')  # P00000004
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
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000001', created_time=datetime.now(),
                              created_by='system')
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000002', created_time=datetime.now(),
                              created_by='system')
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000003', created_time=datetime.now(),
                              created_by='system')
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000004', created_time=datetime.now(),
                              created_by='system')
    click.echo('创建角色权限关联关系成功')


@with_appcontext
def init_menu():
    """初始化菜单
    """
    TMenu.create(menu_no=generate_menu_no(), menu_name='用户管理', level='1', order='1', parent_no='', href='', icon='',
                 state='NORMAL', created_time=datetime.now(), created_by='system')  # M00000001
    click.echo('创建菜单成功')


@with_appcontext
def init_role_menu_rel():
    """初始化角色菜单关联关系
    """
    TRoleMenuRel.create(role_no='R00000001', menu_no='M00000001', created_time=datetime.now(), created_by='system')
    click.echo('创建角色菜单关联关系成功')


@with_appcontext
def init_action_log():
    TActionLog.create(
        action_detail='init',
        action_path=None,
        created_time=datetime.now(),
        created_by='system',
    )
    click.echo('初始化动作日志数据成功')
