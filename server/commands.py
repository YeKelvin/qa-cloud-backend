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
from server.user.model import TUser, TRole, TPermission, TUserRoleRel
from server.user.service import generate_user_no, generate_role_no, generate_permission_no
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
    if drop:
        db.drop_all()
        click.echo('drop tables success')
    db.create_all()
    click.echo('create tables success')


@click.command()
def initdata():
    init_seq()
    init_user()
    click.echo('create initialization data success')


@with_appcontext
def init_seq():
    TSequence.create(seq_name='seq_user_no')
    click.echo('create sequence seq_user_no success')
    TSequence.create(seq_name='seq_role_no')
    click.echo('create sequence seq_role_no success')
    TSequence.create(seq_name='seq_permission_no')
    click.echo('create sequence seq_permission_no success')


@with_appcontext
def init_user():
    admin = TUser()
    admin.user_no = generate_user_no()
    admin.username = 'admin'
    admin.password = admin.generate_password_hash('admin')
    admin.status = 'NORMAL'
    admin.save()
    click.echo('create user admin success')


@with_appcontext
def init_permission():
    TPermission.create(permission_no=generate_permission_no(), endpoint='/register', description='用户注册')
    TPermission.create(permission_no=generate_permission_no(), endpoint='/login', description='用户登录')
    TPermission.create(permission_no=generate_permission_no(), endpoint='/logout', description='用户登出')
    TPermission.create(permission_no=generate_permission_no(), endpoint='/info', description='获取用户信息')


@with_appcontext
def init_role():
    TRole.create(role_no=generate_role_no(), permissions='', description='超级管理员')
    TRole.create(role_no=generate_role_no(), permissions='', description='系统管理员')
    TRole.create(role_no=generate_role_no(), permissions='', description='管理员')
    TRole.create(role_no=generate_role_no(), permissions='', description='帅哥美女')


@with_appcontext
def init_user_role_rel():
    TUserRoleRel.create(user_no='U00000001', role_no='')
