#!/usr/bin/ python3
# @File    : testplan_execution_collection_dao.py
# @Time    : 2021-09-09 19:59:21
# @Author  : Kelvin.Ye
from app.modules.script.model import TTestplanExecutionCollection


def select_by_execution_and_collection(execution_no, collection_no) -> TTestplanExecutionCollection:
    return TTestplanExecutionCollection.filter_by(EXECUTION_NO=execution_no, COLLECTION_NO=collection_no).first()


def select_all_by_execution(execution_no) -> list[TTestplanExecutionCollection]:
    return (
        TTestplanExecutionCollection
        .filter_by(EXECUTION_NO=execution_no)
        .all()
    )


def sum_success_count_by_execution(execution_no):
    return TTestplanExecutionCollection.sum_by(
        field=TTestplanExecutionCollection.SUCCESS_COUNT,
        where=dict(EXECUTION_NO=execution_no)
    )


def sum_failure_count_by_execution(execution_no):
    return TTestplanExecutionCollection.sum_by(
        field=TTestplanExecutionCollection.FAILURE_COUNT,
        where=dict(EXECUTION_NO=execution_no)
    )


def update_running_state_by_execution(execution_no, state):
    TTestplanExecutionCollection.norecord_updates_by(
        values=dict(RUNNING_STATE=state),
        where=dict(EXECUTION_NO=execution_no)
    )
