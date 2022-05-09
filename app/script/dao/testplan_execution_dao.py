#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_execution_dao.py
# @Time    : 2021-09-09 19:58:39
# @Author  : Kelvin.Ye
from app.database import setter
from app.database import where_by
from typing import List

from app.script.enum import RunningState
from app.script.model import TTestplanExecution


def select_by_no(execution_no) -> TTestplanExecution:
    return TTestplanExecution.filter_by(EXECUTION_NO=execution_no).first()


def select_running_by_plan(plan_no) -> TTestplanExecution:
    return TTestplanExecution.filter_by(PLAN_NO=plan_no, RUNNING_STATE=RunningState.RUNNING.value).first()


def select_all_by_plan(plan_no) -> List[TTestplanExecution]:
    return TTestplanExecution.filter_by(PLAN_NO=plan_no).order_by(TTestplanExecution.CREATED_TIME.desc()).all()


def update_running_state_by_no(execution_no, val):
    TTestplanExecution.updates_by(
        setter(RUNNING_STATE=val),
        where_by(EXECUTION_NO=execution_no),
        record=False
    )
