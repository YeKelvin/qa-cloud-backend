#!/usr/bin/ python3
# @File    : element_components_dao.py
# @Time    : 2021-09-06 12:47:41
# @Author  : Kelvin.Ye
from app.modules.script.model import TElementComponents


def select_by_child(child_no) -> TElementComponents:
    return TElementComponents.filter_by(CHILD_NO=child_no).first()


def select_by_parent_and_child(parent_no, child_no) -> TElementComponents:
    return TElementComponents.filter_by(PARENT_NO=parent_no, CHILD_NO=child_no).first()


def select_all_by_parent(parent_no) -> list[TElementComponents]:
    return TElementComponents.filter_by(PARENT_NO=parent_no).all()
