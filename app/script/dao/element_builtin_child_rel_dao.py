#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_builtin_child_rel_dao.py
# @Time    : 2021-09-06 12:47:41
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementBuiltinChildRel


def select_by_child(child_no) -> TElementBuiltinChildRel:
    return TElementBuiltinChildRel.filter_by(CHILD_NO=child_no).first()


def select_by_parent_and_child(parent_no, child_no) -> TElementBuiltinChildRel:
    return TElementBuiltinChildRel.filter_by(PARENT_NO=parent_no, CHILD_NO=child_no).first()


def select_all_by_parent(parent_no) -> List[TElementBuiltinChildRel]:
    return TElementBuiltinChildRel.filter_by(PARENT_NO=parent_no).all()
