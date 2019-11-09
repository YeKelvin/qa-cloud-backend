#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : commands.py.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from server.extensions import db
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
        click.echo('删除所有表成功')
    db.create_all()
    click.echo('创建所有表成功')
