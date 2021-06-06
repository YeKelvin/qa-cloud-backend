#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_element_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from app.script.model import TTestElement


def select_by_elementno(element_no) -> TTestElement:
    return TTestElement.query_by(ELEMENT_NO=element_no).first()
