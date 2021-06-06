#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_property_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementProperty


def select_by_elementno_and_propname(element_no, prop_name) -> TElementProperty:
    return TElementProperty.query_by(ELEMENT_NO=element_no, PROPERTY_NAME=prop_name).first()


def select_all_by_elementno(element_no) -> List[TElementProperty]:
    return TElementProperty.query_by(ELEMENT_NO=element_no).all()
