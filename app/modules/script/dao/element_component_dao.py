#!/usr/bin/ python3
# @File    : element_component_dao.py
# @Time    : 2021-09-06 12:47:41
# @Author  : Kelvin.Ye
from app.modules.script.model import TElementComponent


def select_by_component(element_no) -> TElementComponent:
    return TElementComponent.filter_by(ELEMENT_NO=element_no).first()


def select_by_parent_and_component(parent_no, element_no) -> TElementComponent:
    return TElementComponent.filter_by(PARENT_NO=parent_no, ELEMENT_NO=element_no).first()


def select_all_by_parent(parent_no) -> list[TElementComponent]:
    return TElementComponent.filter_by(PARENT_NO=parent_no).all()


def select_all_by_parent_and_notin_components(parent_no, components) -> list[TElementComponent]:
    return (
        TElementComponent
        .filter(
            TElementComponent.PARENT_NO == parent_no,
            TElementComponent.ELEMENT_NO.notin_(components)
        )
        .all()
    )
