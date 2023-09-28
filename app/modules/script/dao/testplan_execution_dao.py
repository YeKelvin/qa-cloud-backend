#!/usr/bin/ python3
# @File    : testplan_execution_dao.py
# @Time    : 2021-09-09 19:58:39
# @Author  : Kelvin.Ye
from sqlalchemy import select

from app.database import db_scalars
from app.modules.script.enum import RunningState
from app.modules.script.model import TTestplanExecution


def select_by_no(execution_no) -> TTestplanExecution:
    return db_scalars(
        select(TTestplanExecution)
        .where(
            TTestplanExecution.exclude_deleted_data(),
            TTestplanExecution.EXECUTION_NO == execution_no
        )
    ).first()


def select_running_by_plan(plan_no) -> TTestplanExecution:
    return db_scalars(
        select(TTestplanExecution)
        .where(
            TTestplanExecution.exclude_deleted_data(),
            TTestplanExecution.PLAN_NO == plan_no,
            TTestplanExecution.EXECUTION_STATE == RunningState.RUNNING.value
        )
    ).first()


def select_all_by_plan(plan_no) -> list[TTestplanExecution]:
    return db_scalars(
        select(TTestplanExecution)
        .where(
            TTestplanExecution.exclude_deleted_data(),
            TTestplanExecution.PLAN_NO == plan_no
        )
        .order_by(TTestplanExecution.CREATED_TIME.desc())
    ).all()


def update_execution_state(execution_no, state):
    entity = select_by_no(execution_no)
    entity.no_record_update(
        EXECUTION_STATE=state
    )
