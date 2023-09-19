#!/usr/bin/ python3
# @File    : testplan_execution_items_dao.py
# @Time    : 2021-09-09 19:59:21
# @Author  : Kelvin.Ye
from app.modules.script.model import TTestplanExecutionItems


def select_by_execution_and_collection(execution_no, collection_no) -> TTestplanExecutionItems:
    return TTestplanExecutionItems.filter_by(EXECUTION_NO=execution_no, COLLECTION_NO=collection_no).first()


def select_all_by_execution(execution_no) -> list[TTestplanExecutionItems]:
    return TTestplanExecutionItems.filter_by(EXECUTION_NO=execution_no).order_by(TTestplanExecutionItems.SORT_NO).all()


def sum_success_count_by_execution(execution_no):
    return TTestplanExecutionItems.sum_by(
        field=TTestplanExecutionItems.SUCCESS_COUNT,
        where=dict(EXECUTION_NO=execution_no)
    )


def sum_failure_count_by_execution(execution_no):
    return TTestplanExecutionItems.sum_by(
        field=TTestplanExecutionItems.FAILURE_COUNT,
        where=dict(EXECUTION_NO=execution_no)
    )


def update_running_state_by_execution(execution_no, state):
    TTestplanExecutionItems.no_record_updates_by(
        setter=dict(RUNNING_STATE=state),
        where=dict(EXECUTION_NO=execution_no)
    )
