#!/usr/bin/ python3
# @File    : testplan_execution_dao.py
# @Time    : 2021-09-09 19:58:39
# @Author  : Kelvin.Ye
from app.modules.script.enum import RunningState
from app.modules.script.model import TTestplanExecution


def select_by_no(execution_no) -> TTestplanExecution:
    return TTestplanExecution.filter_by(EXECUTION_NO=execution_no).first()


def select_running_by_plan(plan_no) -> TTestplanExecution:
    return TTestplanExecution.filter_by(PLAN_NO=plan_no, RUNNING_STATE=RunningState.RUNNING.value).first()


def select_all_by_plan(plan_no) -> list[TTestplanExecution]:
    return TTestplanExecution.filter_by(PLAN_NO=plan_no).order_by(TTestplanExecution.CREATED_TIME.desc()).all()


def update_running_state_by_no(execution_no, val):
    TTestplanExecution.no_record_updates_by(
        setter=dict(RUNNING_STATE=val),
        where=dict(EXECUTION_NO=execution_no)
    )
