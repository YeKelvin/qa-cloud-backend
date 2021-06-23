#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_property_rel_dao.py
# @Time    : 2021/6/5 11:78
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementPropertyRel


def select_all_by_parentno(parent_no) -> List[TElementPropertyRel]:
    return TElementPropertyRel.query_by(PARENT_NO=parent_no).all()
