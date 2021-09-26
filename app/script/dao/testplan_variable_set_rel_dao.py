#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_variable_set_rel_dao.py
# @Time    : 2021-09-15 18:46:52
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TTestPlanVariableSetRel


def select_all_by_plan(plan_no) -> List[TTestPlanVariableSetRel]:
    return TTestPlanVariableSetRel.filter_by(PLAN_NO=plan_no).all()
