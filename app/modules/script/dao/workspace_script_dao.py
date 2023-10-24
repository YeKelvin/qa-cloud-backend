#!/usr/bin/ python3
# @File    : workspace_script_dao.py
# @Time    : 2021/6/6 11:25
# @Author  : Kelvin.Ye
from app.modules.script.model import TWorkspaceScript


def select_by_script(element_no) -> TWorkspaceScript:
    return TWorkspaceScript.filter_by(ELEMENT_NO=element_no).first()


def select_by_workspace(workspace_no) -> list[TWorkspaceScript]:
    return TWorkspaceScript.filter_by(WORKSPACE_NO=workspace_no).all()
