#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database_config_dao.py
# @Time    : 2022-04-04 17:32:16
# @Author  : Kelvin.Ye
from flask_sqlalchemy import Pagination

from app.script.model import TDatabaseConfig
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(db_no) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(DATABASE_NO=db_no).first()


def select_by_name(db_name) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(DATABASE_NAME=db_name).first()


def select_first(**kwargs) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(**kwargs).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    if kwargs:
        conds.like(TDatabaseConfig.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(TDatabaseConfig.DATABASE_NO, kwargs.pop('databaseNo', None))
        conds.like(TDatabaseConfig.DATABASE_NAME, kwargs.pop('databaseName', None))
        conds.like(TDatabaseConfig.DATABASE_DESC, kwargs.pop('databaseDesc', None))
        conds.like(TDatabaseConfig.DATABASE_TYPE, kwargs.pop('databaseType', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TDatabaseConfig.filter(*conds).order_by(TDatabaseConfig.CREATED_TIME.desc()).paginate(page, page_size)
