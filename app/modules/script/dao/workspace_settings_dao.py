#!/usr/bin python3
# @File    : workspace_settings_dao.py
# @Time    : 2023-06-21 16:16:59
# @Author  : Kelvin.Ye
from app.modules.script.model import TWorkspaceComponentSettings


def select_by_workspace(workspace_no) -> TWorkspaceComponentSettings:
    return TWorkspaceComponentSettings.filter_by(WORKSPACE_NO=workspace_no).first()
