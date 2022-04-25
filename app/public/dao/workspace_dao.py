#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_dao.py
# @Time    : 2021/6/5 23:28
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.public.model import TWorkspace
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(workspace_no) -> TWorkspace:
    return TWorkspace.filter_by(WORKSPACE_NO=workspace_no).first()


def select_by_name(workspace_name) -> TWorkspace:
    return TWorkspace.filter_by(WORKSPACE_NAME=workspace_name).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TWorkspace.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
    conds.like(TWorkspace.WORKSPACE_NAME, kwargs.pop('workspaceName', None))
    conds.like(TWorkspace.WORKSPACE_DESC, kwargs.pop('workspaceDesc', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TWorkspace.filter(
        *conds
    ).group_by(
        TWorkspace.ID,
        TWorkspace.WORKSPACE_SCOPE
    ).order_by(
        TWorkspace.WORKSPACE_SCOPE.desc(),
        TWorkspace.CREATED_TIME.desc()
    ).paginate(
        page,
        page_size
    )


def select_all() -> List[TWorkspace]:
    return TWorkspace.filter_by().order_by(TWorkspace.CREATED_TIME.desc()).all()
