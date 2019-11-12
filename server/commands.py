#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : commands.py.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from server.common.sequence import TSequence
from server.extensions import db
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
    help='drop all table, before initdb'
)
@with_appcontext
def initdb(drop):
    """创建表
    """
    if drop:
        db.drop_all()
        click.echo('drop tables success')
    db.create_all()
    click.echo('create tables success')


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
    click.echo('create initialization data success')


@with_appcontext
def init_seq():
    """初始化序列（SQLite专用）
    """
    TSequence.create(seq_name='seq_user_no')
    click.echo('create sequence seq_user_no success')
    TSequence.create(seq_name='seq_role_no')
    click.echo('create sequence seq_role_no success')
    TSequence.create(seq_name='seq_permission_no')
    click.echo('create sequence seq_permission_no success')


@with_appcontext
def init_user():
    """初始化用户
    """
    admin = TUser()
    admin.user_no = generate_user_no()  # U00000001
    admin.username = 'admin'
    admin.password = admin.generate_password_hash('admin')
    admin.status = 'NORMAL'
    admin.save()
    click.echo('create user admin success')


@with_appcontext
def init_role():
    """初始化角色
    """
    TRole.create(role_no=generate_role_no(), role_name='超级管理员')  # R00000001
    TRole.create(role_no=generate_role_no(), role_name='系统管理员')  # R00000002
    TRole.create(role_no=generate_role_no(), role_name='管理员')  # R00000003
    TRole.create(role_no=generate_role_no(), role_name='帅哥美女')  # R00000004


@with_appcontext
def init_permission():
    """初始化权限
    """
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户注册', module='/user',
                       endpoint='/register')  # P00000001
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登录', module='/user',
                       endpoint='/login')  # P00000002
    TPermission.create(permission_no=generate_permission_no(), permission_name='用户登出', module='/user',
                       endpoint='/logout')  # P00000003
    TPermission.create(permission_no=generate_permission_no(), permission_name='获取用户信息', module='/user',
                       endpoint='/info')  # P00000004


@with_appcontext
def init_user_role_rel():
    """初始化用户角色关联关系
    """
    TUserRoleRel.create(user_no='U00000001', role_no='R00000001')


@with_appcontext
def init_role_permission_rel():
    """初始化角色权限关联关系
    """
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000001')
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000002')
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000003')
    TRolePermissionRel.create(role_no='R00000001', permission_no='P00000004')


@with_appcontext
def init_menu():
    """初始化菜单
    """
    TMenu.create(menu_no=generate_menu_no(), menu_name='用户管理', level='1', order='1', parent_no='', href='', icon='',
                 state='NORMAL')  # M00000001


@with_appcontext
def init_role_menu_rel():
    """初始化角色菜单关联关系
    """
    TRoleMenuRel.create(role_no='R00000001', menu_no='M00000001')
