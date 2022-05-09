#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_dao.py
# @Time    : 2021-09-09 19:58:39
# @Author  : Kelvin.Ye
from app.script.model import TTestplan


def select_by_no(plan_no) -> TTestplan:
    return TTestplan.filter_by(PLAN_NO=plan_no).first()
