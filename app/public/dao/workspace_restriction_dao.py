#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_restriction_dao.py
# @Time    : 2022/4/22 15:50
# @Author  : Kelvin.Ye
from typing import List

from app.public.model import TWorkspaceRestriction


def select_by_workspace_and_permission(workspace_no, permission_no) -> TWorkspaceRestriction:
    return TWorkspaceRestriction.filter_by(WORKSPACE_NO=workspace_no, PERMISSION_NO=permission_no).first()


def select_all_by_workspace(workspace_no) -> List[TWorkspaceRestriction]:
    return TWorkspaceRestriction.filter_by(WORKSPACE_NO=workspace_no).all()


def delete_all_by_workspace_and_notin_permission(workspace_no, *permission_numbers):
    TWorkspaceRestriction.deletes(
        TWorkspaceRestriction.WORKSPACE_NO == workspace_no,
        TWorkspaceRestriction.PERMISSION_NO.notin_(*permission_numbers)
    )
