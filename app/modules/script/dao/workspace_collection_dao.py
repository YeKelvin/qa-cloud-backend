#!/usr/bin/ python3
# @File    : workspace_collection_dao.py
# @Time    : 2021/6/6 11:25
# @Author  : Kelvin.Ye
from app.modules.script.model import TWorkspaceCollection


def select_by_collection(collection_no) -> TWorkspaceCollection:
    return TWorkspaceCollection.filter_by(COLLECTION_NO=collection_no).first()


def select_by_workspace(workspace_no) -> list[TWorkspaceCollection]:
    return TWorkspaceCollection.filter_by(WORKSPACE_NO=workspace_no).all()
