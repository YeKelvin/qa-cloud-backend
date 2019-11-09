#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : commands.py.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click

from server.utils.log_util import get_logger

log = get_logger(__name__)


@click.command()
@click.option(
    "-d",
    "--drop",
    default=True,
    is_flag=True,
    help="drop all table, before initdb",
)
def initdb():
    pass
