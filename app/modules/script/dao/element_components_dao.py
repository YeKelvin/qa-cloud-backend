#!/usr/bin/ python3
# @File    : element_components_dao.py
# @Time    : 2021-09-06 12:47:41
# @Author  : Kelvin.Ye
from app.modules.script.model import TElementComponents


def select_by_component(element_no) -> TElementComponents:
    return TElementComponents.filter_by(ELEMENT_NO=element_no).first()


def select_by_parent_and_component(parent_no, element_no) -> TElementComponents:
    return TElementComponents.filter_by(PARENT_NO=parent_no, ELEMENT_NO=element_no).first()


def select_all_by_parent(parent_no) -> list[TElementComponents]:
    return TElementComponents.filter_by(PARENT_NO=parent_no).all()
