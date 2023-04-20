#!/usr/bin/ python3
# @File    : test_element_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from app.modules.script.model import TTestElement


def select_by_no(element_no) -> TTestElement:
    return TTestElement.filter_by(ELEMENT_NO=element_no).first()
