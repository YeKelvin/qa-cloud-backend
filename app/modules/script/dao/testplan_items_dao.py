#!/usr/bin/ python3
# @File    : testplan_items_dao.py
# @Time    : 2021-09-09 19:59:21
# @Author  : Kelvin.Ye
from typing import List

from app.modules.script.model import TTestplanItems


def select_by_plan_and_collection(plan_no, collection_no) -> TTestplanItems:
    return TTestplanItems.filter_by(PLAN_NO=plan_no, COLLECTION_NO=collection_no).first()


def select_all_by_plan(plan_no) -> List[TTestplanItems]:
    return TTestplanItems.filter_by(PLAN_NO=plan_no).order_by(TTestplanItems.SORT_NO).all()


def delete_all_by_plan_and_not_in_collection(plan_no, *collection_nos):
    TTestplanItems.deletes(
        TTestplanItems.PLAN_NO == plan_no,
        TTestplanItems.COLLECTION_NO.notin_(*collection_nos)
    )
