#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_children_dao.py
# @Time    : 2021/6/5 11:28
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TElementChildren


def select_by_child(child_no) -> TElementChildren:
    return TElementChildren.filter_by(CHILD_NO=child_no).first()


def select_by_parent_and_child(parent_no, child_no) -> TElementChildren:
    return TElementChildren.filter_by(PARENT_NO=parent_no, CHILD_NO=child_no).first()


def select_by_parent_and_sortno(parent_no, sort_no) -> TElementChildren:
    return TElementChildren.filter_by(PARENT_NO=parent_no, SORT_NO=sort_no).first()


def count_by_parent(parent_no) -> int:
    return TElementChildren.count_by(PARENT_NO=parent_no)


def next_serial_number_by_parent(parent_no) -> int:
    return TElementChildren.count_by(PARENT_NO=parent_no) + 1


def select_all_by_parent(parent_no) -> List[TElementChildren]:
    return TElementChildren.filter_by(PARENT_NO=parent_no).order_by(TElementChildren.SORT_NO).all()
