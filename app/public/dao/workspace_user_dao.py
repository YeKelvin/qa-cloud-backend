#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_dao.py
# @Time    : 2021/6/5 23:27
# @Author  : Kelvin.Ye
from typing import List

from app.public.model import TWorkspaceUser


def select_by_workspace_and_user(workspace_no, user_no) -> TWorkspaceUser:
    return TWorkspaceUser.filter_by(WORKSPACE_NO=workspace_no, USER_NO=user_no).first()


def count_by_workspace(workspace_no) -> int:
    return TWorkspaceUser.count_by(WORKSPACE_NO=workspace_no)


def select_all_by_user(user_no) -> List[TWorkspaceUser]:
    return TWorkspaceUser.filter_by(USER_NO=user_no).all()


def delete_all_by_workspace_and_notin_user(workspace_no, *args) -> None:
    TWorkspaceUser.deletes(
        TWorkspaceUser.WORKSPACE_NO == workspace_no,
        TWorkspaceUser.USER_NO.notin_(*args)
    )
