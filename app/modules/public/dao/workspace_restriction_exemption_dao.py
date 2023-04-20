#!/usr/bin/ python3
# @File    : workspace_restriction_exemption_dao.py
# @Time    : 2022/4/22 15:51
# @Author  : Kelvin.Ye
from app.modules.public.model import TWorkspaceRestrictionExemption


def select_by_workspace(workspace_no) -> TWorkspaceRestrictionExemption:
    return TWorkspaceRestrictionExemption.filter_by(WORKSPACE_NO=workspace_no).first()
