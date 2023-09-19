#!/usr/bin/ python3
# @File    : workspace_dao.py
# @Time    : 2021/6/5 23:28
# @Author  : Kelvin.Ye
from app.modules.public.model import TWorkspace


def select_by_no(workspace_no) -> TWorkspace:
    return TWorkspace.filter_by(WORKSPACE_NO=workspace_no).first()


def select_by_name(workspace_name) -> TWorkspace:
    return TWorkspace.filter_by(WORKSPACE_NAME=workspace_name).first()


def select_all() -> list[TWorkspace]:
    return TWorkspace.filter_by().order_by(TWorkspace.CREATED_TIME.desc()).all()
