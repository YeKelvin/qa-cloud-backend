#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_child_rel_dao.py
# @Time    : 2021/6/5 11:28
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementChildRel


def select_by_childno(child_no) -> TElementChildRel:
    return TElementChildRel.query_by(CHILD_NO=child_no).first()


def select_all_by_parentno(parent_no) -> List[TElementChildRel]:
    return TElementChildRel.query_by(PARENT_NO=parent_no).order_by(TElementChildRel.CHILD_ORDER).all()


def select_by_parentno_and_childno(parent_no, child_no) -> TElementChildRel:
    return TElementChildRel.query_by(PARENT_NO=parent_no, CHILD_NO=child_no).first()


def select_by_type_and_inside(parent_no, child_type) -> TElementChildRel:
    return TElementChildRel.query_by(PARENT_NO=parent_no, CHILD_TYPE=child_type, INSIDE=True).first()


def select_by_parentno_and_childorder(parent_no, child_order) -> TElementChildRel:
    return TElementChildRel.query_by(PARENT_NO=parent_no, CHILD_ORDER=child_order).first()


def count_by_parentno(parent_no) -> int:
    return TElementChildRel.query_by(PARENT_NO=parent_no).count()


def count_by_parentno_and_childtype(parent_no, child_type) -> int:
    return TElementChildRel.query_by(PARENT_NO=parent_no, CHILD_TYPE=child_type).count()


def next_order_by_parentno(parent_no) -> int:
    return TElementChildRel.query_by(PARENT_NO=parent_no).count() + 1
