#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_property_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementProperty


def select_by_propertyno(property_no) -> TElementProperty:
    return TElementProperty.query_by(PROPERTY_NO=property_no).first()




def select_all_by_propertyno(element_no) -> List[TElementProperty]:
    return TElementProperty.query_by(ELEMENT_NO=element_no).all()
