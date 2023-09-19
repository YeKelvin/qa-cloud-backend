#!/usr/bin/ python3
# @File    : element_property_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from app.modules.script.model import TElementProperty


def select_by_element_and_name(element_no, property_name) -> TElementProperty:
    return TElementProperty.filter_by(ELEMENT_NO=element_no, PROPERTY_NAME=property_name).first()


def select_all_by_element(element_no) -> list[TElementProperty]:
    return TElementProperty.filter_by(ELEMENT_NO=element_no).all()


def select_all_by_enable_element(element_no) -> list[TElementProperty]:
    return TElementProperty.filter_by(ELEMENT_NO=element_no, ENABLED=True).all()


def delete_all_by_element_and_notin_name(element_no, *name):
    TElementProperty.deletes(
        TElementProperty.ELEMENT_NO == element_no,
        TElementProperty.PROPERTY_NAME.notin_(*name)
    )
