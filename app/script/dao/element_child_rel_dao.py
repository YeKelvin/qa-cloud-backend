#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_child_rel_dao.py
# @Time    : 2021/6/5 11:28
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementChildRel


def select_by_child(child_no) -> TElementChildRel:
    return TElementChildRel.query_by(CHILD_NO=child_no).first()


def select_by_parent_and_child(parent_no, child_no) -> TElementChildRel:
    return TElementChildRel.query_by(PARENT_NO=parent_no, CHILD_NO=child_no).first()


def select_by_parent_and_serialno(parent_no, serial_no) -> TElementChildRel:
    return TElementChildRel.query_by(PARENT_NO=parent_no, SERIAL_NO=serial_no).first()


def count_by_parent(parent_no) -> int:
    return TElementChildRel.query_by(PARENT_NO=parent_no).count()


def next_serialno_by_parent(parent_no) -> int:
    return TElementChildRel.query_by(PARENT_NO=parent_no).count() + 1


def select_all_by_parent(parent_no) -> List[TElementChildRel]:
    return TElementChildRel.query_by(PARENT_NO=parent_no).order_by(TElementChildRel.SERIAL_NO).all()


def select_all_by_parent_and_greater_than_serialno(parent_no, serial_no) -> List[TElementChildRel]:
    return TElementChildRel.query.filter(
        TElementChildRel.PARENT_NO == parent_no, TElementChildRel.SERIAL_NO > serial_no
    ).order_by(TElementChildRel.SERIAL_NO).all()


def select_all_by_parent_and_less_than_serialno(parent_no, serial_no) -> List[TElementChildRel]:
    return TElementChildRel.query.filter(
        TElementChildRel.PARENT_NO == parent_no, TElementChildRel.SERIAL_NO < serial_no
    ).order_by(TElementChildRel.SERIAL_NO).all()
