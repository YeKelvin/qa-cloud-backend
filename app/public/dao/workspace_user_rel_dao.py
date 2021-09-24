#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_rel_dao.py
# @Time    : 2021/6/5 23:27
# @Author  : Kelvin.Ye
from flask_sqlalchemy import Pagination

from app.public.model import TWorkspaceUserRel


def select_by_workspace_and_user(workspace_no, user_no) -> TWorkspaceUserRel:
    return TWorkspaceUserRel.filter_by(WORKSPACE_NO=workspace_no, USER_NO=user_no).first()


def select_list_by_workspace(**kwargs) -> Pagination:
    return TWorkspaceUserRel.filter_by(
        WORKSPACE_NO=kwargs.pop('workspaceNo')).order_by(
            TWorkspaceUserRel.CREATED_TIME.desc()).paginate(kwargs.pop('page'), kwargs.pop('pageSize'))
