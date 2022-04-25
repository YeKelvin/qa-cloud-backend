#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database_config_dao.py
# @Time    : 2022-04-04 17:32:16
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.script.model import TDatabaseConfig
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(config_no) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(CONFIG_NO=config_no).first()


def select_by_name(config_name) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(CONFIG_NAME=config_name).first()


def select_first(**kwargs) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(**kwargs).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TDatabaseConfig.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
    conds.like(TDatabaseConfig.CONFIG_NO, kwargs.pop('configNo', None))
    conds.like(TDatabaseConfig.CONFIG_NAME, kwargs.pop('configName', None))
    conds.like(TDatabaseConfig.CONFIG_DESC, kwargs.pop('configDesc', None))
    conds.like(TDatabaseConfig.DATABASE_TYPE, kwargs.pop('databaseType', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TDatabaseConfig.filter(*conds).order_by(TDatabaseConfig.CREATED_TIME.desc()).paginate(page, page_size)


def select_all(**kwargs) -> List[TDatabaseConfig]:
    conds = QueryCondition()
    if kwargs:
        conds.like(TDatabaseConfig.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(TDatabaseConfig.CONFIG_NO, kwargs.pop('configNo', None))
        conds.like(TDatabaseConfig.CONFIG_NAME, kwargs.pop('configName', None))
        conds.like(TDatabaseConfig.CONFIG_DESC, kwargs.pop('configDesc', None))
        conds.like(TDatabaseConfig.DATABASE_TYPE, kwargs.pop('databaseType', None))

    return TDatabaseConfig.filter(*conds).order_by(TDatabaseConfig.CREATED_TIME.desc()).all()
