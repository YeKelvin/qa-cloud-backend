#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_dao.py
# @Time    : 2021/6/5 23:27
# @Author  : Kelvin.Ye
from flask_sqlalchemy import Pagination

from app.public.model import TWorkspaceUser


def select_by_workspace_and_user(workspace_no, user_no) -> TWorkspaceUser:
    return TWorkspaceUser.filter_by(WORKSPACE_NO=workspace_no, USER_NO=user_no).first()


def select_list_by_workspace(**kwargs) -> Pagination:
    return TWorkspaceUser.filter_by(
        WORKSPACE_NO=kwargs.pop('workspaceNo')).order_by(
            TWorkspaceUser.CREATED_TIME.desc()).paginate(kwargs.pop('page'), kwargs.pop('pageSize'))


def delete_all_by_workspace_and_notin_user(workspace_no, *user_no) -> None:
    TWorkspaceUser.filter(
        TWorkspaceUser.WORKSPACE_NO == workspace_no,
        TWorkspaceUser.USER_NO.notin_(*user_no)
    ).update({TWorkspaceUser.DELETED: 1})
