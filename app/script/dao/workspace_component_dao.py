#!/usr/bin/ python3
# @File    : workspace_component_dao.py
# @Time    : 2022/9/22 11:14
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TWorkspaceComponent


def select_by_component(component_no) -> TWorkspaceComponent:
    return TWorkspaceComponent.filter_by(COMPONENT_NO=component_no).first()


def select_by_workspace_and_component(workspace_no, component_no) -> TWorkspaceComponent:
    return TWorkspaceComponent.filter_by(WORKSPACE_NO=workspace_no, COMPONENT_NO=component_no).first()


def select_all_by_workspace(workspace_no) -> List[TWorkspaceComponent]:
    return (
        TWorkspaceComponent
        .filter_by(WORKSPACE_NO=workspace_no)
        .order_by(TWorkspaceComponent.SORT_WEIGHT.desc(), TWorkspaceComponent.SORT_NUMBER.asc())
        .all()
    )
