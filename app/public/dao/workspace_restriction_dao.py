#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_restriction_dao.py
# @Time    : 2022/4/22 15:50
# @Author  : Kelvin.Ye
from typing import List

from app.public.model import TWorkspaceRestriction


def select_by_restriction(restriction_no) -> TWorkspaceRestriction:
    return TWorkspaceRestriction.filter_by(RESTRICTION_NO=restriction_no).first()


def select_first(**kwargs) -> TWorkspaceRestriction:
    return TWorkspaceRestriction.filter_by(**kwargs).first()


def select_all_by_workspace(workspace_no) -> List[TWorkspaceRestriction]:
    return TWorkspaceRestriction.filter_by(WORKSPACE_NO=workspace_no).all()
