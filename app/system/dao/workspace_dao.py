#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_dao.py
# @Time    : 2021/6/5 23:28
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.system.model import TWorkspace
from app.utils.sqlalchemy_util import QueryCondition


def select_by_workspaceno(workspace_no) -> TWorkspace:
    return TWorkspace.query_by(WORKSPACE_NO=workspace_no).first()


def select_by_workspacename(workspace_name) -> TWorkspace:
    return TWorkspace.query_by(WORKSPACE_NAME=workspace_name).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition(TWorkspace)
    if kwargs:
        conds.add_fuzzy_match(TWorkspace.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.add_fuzzy_match(TWorkspace.WORKSPACE_NAME, kwargs.pop('workspaceName', None))
        conds.add_fuzzy_match(TWorkspace.WORKSPACE_TYPE, kwargs.pop('workspaceType', None))
        conds.add_fuzzy_match(TWorkspace.WORKSPACE_DESC, kwargs.pop('workspaceDesc', None))

    page = kwargs.pop('page')
    pageSize = kwargs.pop('pageSize')

    return TWorkspace.query.filter(*conds).order_by(TWorkspace.CREATED_TIME.desc()).paginate(page, pageSize)


def select_all() -> List[TWorkspace]:
    return TWorkspace.query_by().order_by(TWorkspace.CREATED_TIME.desc()).all()
