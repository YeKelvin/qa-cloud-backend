#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_dao.py
# @Time    : 2021-09-09 19:58:39
# @Author  : Kelvin.Ye
from app.script.model import TTestPlan


def select_by_no(plan_no) -> TTestPlan:
    return TTestPlan.query_by(PLAN_NO=plan_no).first()


def update_running_state_by_no(plan_no, val):
    TTestPlan.query_by(PLAN_NO=plan_no).update({'RUNNING_STATE': val})
