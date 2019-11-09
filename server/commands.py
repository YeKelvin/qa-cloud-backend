#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : commands.py.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from server.common.sequence import TSequence
from server.extensions import db
from server.user.model import TUser
from server.user.service import generate_user_no
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
def init_user():
    admin = TUser()
    admin.user_no = generate_user_no()
    admin.username = 'admin'
    admin.password = admin.generate_password_hash('admin')
    admin.status = 'NORMAL'
    admin.save()
    click.echo('create user admin success')


@with_appcontext
def init_seq():
    TSequence.create(seq_name='seq_user_no')
    click.echo('create sequence seq_user_no success')
    TSequence.create(seq_name='seq_role_no')
    click.echo('create sequence seq_role_no success')
    TSequence.create(seq_name='seq_permission_no')
    click.echo('create sequence seq_permission_no success')
