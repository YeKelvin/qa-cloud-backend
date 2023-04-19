#!/usr/bin/ python3
# @File    : element_options_dao.py
# @Time    : 2022/10/18 18:17
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementOptions


def select_by_element_and_name(element_no, option_name) -> TElementOptions:
    return TElementOptions.filter_by(ELEMENT_NO=element_no, OPTION_NAME=option_name).first()


def select_all_by_element(element_no) -> List[TElementOptions]:
    return TElementOptions.filter_by(ELEMENT_NO=element_no).all()


def delete_all_by_element_and_notin_name(element_no, *name):
    TElementOptions.deletes(
        TElementOptions.ELEMENT_NO == element_no,
        TElementOptions.OPTION_NAME.notin_(*name)
    )
