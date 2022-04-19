#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_items_dao.py
# @Time    : 2021-09-09 19:59:21
# @Author  : Kelvin.Ye
from typing import List

from app.database import setter
from app.database import where_by
from app.script.model import TTestplanExecutionItems


def select_by_execution_and_collection(execution_no, collection_no) -> TTestplanExecutionItems:
    return TTestplanExecutionItems.filter_by(EXECUTION_NO=execution_no, COLLECTION_NO=collection_no).first()


def select_all_by_execution(execution_no) -> List[TTestplanExecutionItems]:
    return TTestplanExecutionItems.filter_by(EXECUTION_NO=execution_no).order_by(TTestplanExecutionItems.SORT_NO).all()


def update_running_state_by_execution(execution_no, state) -> None:
    TTestplanExecutionItems.updates_by(
        setter(RUNNING_STATE=state),
        where_by(EXECUTION_NO=execution_no),
        record=False
    )
